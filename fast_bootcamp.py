"""CPU-bounded runtime profile for the zero-cost GitHub-hosted bootcamp.

Keeps the pedagogical round count intact while bounding context/output so a small
local model can complete within an ordinary ChatGPT-triggered workflow window.
"""
from __future__ import annotations

import json
import time

import requests

import bootcamp
import quality_gate


_ORIGINAL_SELECT = bootcamp.select_source_segments


def bounded_select_source_segments(text: str, limit: int = 3000) -> str:
    return _ORIGINAL_SELECT(text, min(limit, 1500))


TOKEN_CAPS = {
    bootcamp.SOURCE_SYNTH_SYSTEM: 650,
    bootcamp.ARCHITECT_SYSTEM: 550,
    bootcamp.CURRICULUM_SYSTEM: 1100,
    bootcamp.STUDENT_SYSTEM: 425,
    bootcamp.EXAMINER_SYSTEM: 325,
    bootcamp.TRANSFER_SYSTEM: 550,
    bootcamp.DISTILLER_SYSTEM: 800,
}

SINGLE_TRANSFER_SYSTEM = """You are TRANSFER EXAM DESIGNER. Create exactly ONE novel practitioner task that combines at least two supplied capabilities and does not reuse the training scenarios. Return ONLY strict JSON: {\"rounds\":[{\"task\":\"...\",\"capability_ids\":[\"...\"],\"hidden_rubric\":[\"short check\"],\"adversarial\":false,\"critical\":true}]}. The second requested exam should contain a tempting false premise or unsafe shortcut."""


def bounded_llm(system: str, user: str, max_tokens: int = 500, temperature: float = 0.2) -> str:
    effective_max = min(max_tokens, TOKEN_CAPS.get(system, 500))
    payload = {
        "model": bootcamp.MODEL_NAME,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user + "\n/no_think"},
        ],
        "temperature": temperature,
        "max_tokens": effective_max,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    last = None
    for attempt in range(2):
        try:
            response = requests.post(bootcamp.LLM_URL, json=payload, timeout=150)
            response.raise_for_status()
            return bootcamp.strip_thinking(response.json()["choices"][0]["message"]["content"])
        except Exception as exc:
            last = exc
            time.sleep(2 + 2 * attempt)
    raise RuntimeError(f"bounded local model call failed: {last}")


def robust_build_transfer_tasks(spec, caps, curriculum):
    prior = [task["task"] for task in curriculum]
    tasks = []
    for number in (1, 2):
        obj = bootcamp.json_llm(
            SINGLE_TRANSFER_SYSTEM,
            f"FUNCTION: {spec['function']}\nTRANSFER EXAM NUMBER: {number}\nCAPABILITIES:\n{bootcamp.capability_snapshot(caps)}\nPRIOR TRAINING TASKS (do not reuse):\n{json.dumps(prior)}\nCreate exactly one distinct transfer task. Exam 2 must be adversarial.",
            max_tokens=500,
            temperature=0.35,
        )
        task = bootcamp.validate_curriculum(obj, 1, caps)[0]
        if number == 2:
            task["adversarial"] = True
        tasks.append(task)
        prior.append(task["task"])
    return tasks


def conservative_distill(spec, knowledge, caps, lessons, qual):
    return quality_gate.build_capsule(spec, knowledge, caps, lessons, qual)


bootcamp.select_source_segments = bounded_select_source_segments
bootcamp.llm = bounded_llm
bootcamp.build_transfer_tasks = robust_build_transfer_tasks
bootcamp.qualify = quality_gate.conservative_qualification
bootcamp.distill = conservative_distill
bootcamp.write_outputs = quality_gate.write_outputs


if __name__ == "__main__":
    bootcamp.main()
