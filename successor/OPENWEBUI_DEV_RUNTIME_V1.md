# Vera V3 Open WebUI Development Runtime V1

Date: 2026-09-20

Status: development runtime only. This is not Task 11 qualification, promotion, production approval, or canonical installation.

Repository: `thebrazenbeard/vera_model_training`
Serving branch: `work/bv-openwebui-peft-server-20260920`
Exact serving-code head validated: `38988490d1baed87f6122ad02fb27aa97e6e68f6`
Focused proxy tests: `13/13 PASS`
Full repository suite: `216/216 PASS`
Python compile: `PASS`

## Runtime inputs

Base model: `C:\Vera\models\base\SmolLM3-3B`
Full PEFT adapter: `C:\Vera\successor\private\successor_v3\VERA_SUCCESSOR_V3_DEV_R1_20260919\full`

## Converter provenance

llama.cpp source commit: `ce8caa6e60a03093351d6016a818720e0d46f0fb`
Installed Windows package: `ggml.llamacpp` version `b11026`

## Frozen deployment artifacts

- Base GGUF: `C:\Vera\successor\deploy\vera-v3-base-q8_0.gguf`
  - bytes: `3275575168`
  - SHA-256: `27a85369dfe51fb5bc74a5671373da130ca3d28d434127aa5eedd8e19dfbbce6`
- Full LoRA GGUF: `C:\Vera\successor\deploy\vera-v3-full-adapter-f16.gguf`
  - bytes: `60491776`
  - SHA-256: `01bf9bee07527200faba0b204668c69cdd5739260a4ab9f56820893bc2948930`

Deployment composite digest (SHA-256 of `<base_sha>\n<adapter_sha>`):
`4d526d945ea537e9f34ab4041c4441c130979b4646c7e89039cb002e44b4e366`

## Conversion commands

`py -3.11 C:\Vera\tools\llama.cpp\convert_hf_to_gguf.py C:\Vera\models\base\SmolLM3-3B --outfile C:\Vera\successor\deploy\vera-v3-base-q8_0.gguf --outtype q8_0`

`py -3.11 C:\Vera\tools\llama.cpp\convert_lora_to_gguf.py --base C:\Vera\models\base\SmolLM3-3B --outfile C:\Vera\successor\deploy\vera-v3-full-adapter-f16.gguf --outtype f16 C:\Vera\successor\private\successor_v3\VERA_SUCCESSOR_V3_DEV_R1_20260919\full`

## Local serving topology

llama.cpp backend: `127.0.0.1:11435`
Open WebUI-facing proxy: `127.0.0.1:11436`
OpenAI base URL: `http://127.0.0.1:11436/v1`
Model ID: `vera-v3-full-dev`

Backend launch shape:
`llama-server -m C:\Vera\successor\deploy\vera-v3-base-q8_0.gguf --lora C:\Vera\successor\deploy\vera-v3-full-adapter-f16.gguf -ngl 0 -c 8192 --host 127.0.0.1 --port 11435 --jinja`

Proxy launch shape:
`py -3.11 -m successor.openwebui_server --upstream-url http://127.0.0.1:11435 --candidate-digest 4d526d945ea537e9f34ab4041c4441c130979b4646c7e89039cb002e44b4e366 --model-id vera-v3-full-dev --host 127.0.0.1 --port 11436`

## Behavioral verification

The real GGUF+LoRA subject produced valid OpenAI `message.tool_calls` through the proxy.
A two-turn tool loop passed: tool request -> normalized OpenAI tool call -> simulated tool result -> final Vera answer.
The final endpoint was rechecked on port 11436 and again returned `finish_reason = tool_calls` with `get_current_time` and `{"timezone":"UTC"}`.

Observed CPU inference after load was roughly 7-10 tokens/second.

The validated machine had no usable CUDA device during this run, so the verified serving subject is CPU-only. That is runtime state, not a permanent model requirement.

Open WebUI Computer (`cptr` 0.9.21) was subsequently started natively on `127.0.0.1:8000`. A separate `Vera V3 Full Dev` OpenAI connection was added through Computer's own config store with `provider_type=llama.cpp`, base URL `http://127.0.0.1:11436/v1`, and an explicit model whitelist containing only `vera-v3-full-dev`. Existing OpenAI and `Local-Vera-v1` connections were preserved.

Computer's own `cptr.utils.ai.stream_openai_completions()` parser was then executed against the live connection. It emitted a native Computer event sequence containing `type=tool_call`, name `get_current_time`, arguments `{"timezone":"UTC"}`, followed by `type=done`. This validates the actual Computer streaming/tool parser, not only the proxy API surface.

The proxy is deliberately loopback-only. If Open WebUI later runs in Docker, container reachability and authentication should be chosen explicitly rather than silently widening the bind address.