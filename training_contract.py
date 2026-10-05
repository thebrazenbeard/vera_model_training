from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

class ContractError(ValueError):
    pass

CANONICAL_CONTRACT_SEMANTIC_SHA256 = "76d7fafa6270069ed9f52a20e9719c8d9ed233643f739c779b82b5119960bfce"

def _strict_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ContractError(f'duplicate key: {key}')
        out[key] = value
    return out

def load_contract(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_strict_pairs)
    except json.JSONDecodeError as exc:
        raise ContractError(f'invalid json: {exc}') from exc

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)

def _semantic_digest(data: dict[str, Any]) -> str:
    payload = json.dumps(
        data,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    ).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def validate_contract(data: dict[str, Any]) -> None:
    require(data.get('schema') == 'VERA_EXECUTION_CONTRACT_V1', 'wrong schema')
    require(data.get('execution_precedence') == 'THIS_CONTRACT_IS_SOLE_EXECUTION_NORMATIVE_SOURCE', 'execution precedence missing')
    require(data['source']['repository'] == 'thebrazenbeard/vera_model_training', 'wrong repository')
    require(data['source']['parent_head'] == 'c06e33d44184904418a4a68f22f78d19a4f46137', 'wrong parent head')
    require(data['authorization']['requires_live_operator_authorization'] is True, 'live authorization gate missing')

    expected_stages = [
        'stage0_runtime', 'stage1_corpus', 'stage2_eval', 'stage3_h0',
        'stage4_mechanisms', 'stage5_corrigibility_identity', 'stage6_epistemic',
        'stage7_tools', 'stage8_reasoning', 'stage9_continual', 'stage10_routing',
        'stage11_novel_task', 'stage12_adaptive_latent', 'stage13_preference',
        'stage14_integration', 'stage15_independent_review',
        'stage16_protected_qualification', 'stage17_release',
    ]
    require([s['id'] for s in data['stages']] == expected_stages, 'stage sequence mismatch')

    isolation = data['controls']['fresh_state_isolation']
    require(isolation['required'] is True, 'fresh-state isolation must be required')
    require(isolation['weaker_fallback_allowed'] is False, 'weaker isolation fallback forbidden')
    require(isolation['implementation_owner'] == 'Lane-C', 'isolation owner must remain Lane-C')
    require('reserved_branch' not in isolation, 'stale C branch pin is forbidden')
    c_binding = isolation['accepted_subject_binding']
    require(c_binding['status'] in {'PENDING_VERA_ACCEPTANCE', 'ACCEPTED'}, 'invalid C subject acceptance state')
    require(c_binding['acceptance_authority'] == 'Vera', 'C subject acceptance authority must be Vera')
    require(c_binding['exact_head_required'] is True, 'C subject must bind an exact head')
    if c_binding['status'] == 'PENDING_VERA_ACCEPTANCE':
        require(c_binding['accepted_subject'] is None, 'pending C binding cannot claim an accepted subject')
    else:
        accepted = c_binding['accepted_subject']
        require(isinstance(accepted, dict), 'accepted C subject must be an object')
        require(accepted.get('repository') == 'thebrazenbeard/vera_model_training', 'accepted C repository mismatch')
        require(isinstance(accepted.get('branch'), str) and bool(accepted['branch'].strip()), 'accepted C branch missing')
        head = accepted.get('head')
        require(isinstance(head, str) and len(head) == 40 and all(ch in '0123456789abcdef' for ch in head), 'accepted C head must be exact lowercase SHA-1')

    expected_canaries = [
        'undeclared_environment_global_counter',
        'changed_file_outside_arm_root',
        'shared_retrieval_index_or_external_mutable_state',
        'inherited_write_capable_credential',
        'reused_daemon_port_or_provider_session_state',
        'stale_adapter_module_resurrection',
        'deterministic_state_file_outside_isolated_root',
    ]
    require(isolation['mandatory_canaries'] == expected_canaries, 'mandatory isolation canaries changed or incomplete')

    expected_covered_channels = {
        'environment_variables', 'temp_home_cache', 'local_databases',
        'retrieval_indexes', 'external_services', 'provider_session_state',
        'shared_credentials', 'ports_daemons', 'model_server_sessions',
        'deterministic_filenames', 'process_globals_rng',
    }
    require(set(isolation['covered_channels']) == expected_covered_channels, 'isolation covered channels changed or incomplete')

    correction = data['controls']['corrigibility_identity_gate']
    require(correction['ordering'] == 'CORRIGIBILITY_BEFORE_OR_JOINT_WITH_IDENTITY', 'corrigibility ordering ambiguous')
    require(correction['promotion_requires_joint_pass'] is True, 'identity promotion not jointly gated')

    stage0 = data['stage0']
    require(stage0['smoke']['exactly_one_optimizer_step'] is True, 'Stage-0 smoke must use one optimizer step')
    require(stage0['smoke']['prove_trainable_digest_changed'] is True, 'Stage-0 digest proof missing')
    require(stage0['soak']['minimum_optimizer_steps'] >= 20, 'Stage-0 soak too short')
    require(stage0['soak']['maximum_wall_minutes'] <= 15, 'Stage-0 soak not bounded')
    require(stage0['soak']['workload_dimensions_must_be_frozen_in_subject'] is True, 'Stage-0 workload not frozen')
    for key in ('cpu_fallback', 'driver_reset_or_cuda_error', 'cuda_allocation_failure', 'commit_headroom_breach', 'thermal_limit_breach', 'step_time_degradation'):
        require(stage0['abort'][key] is True, f'Stage-0 abort gate missing: {key}')
    require(stage0['thresholds'] == {
        'minimum_commit_headroom_mib': 4096,
        'gpu_temperature_c_abort': 88,
        'step_time_p95_over_median_abort_ratio': 1.5,
        'consecutive_degraded_steps': 5,
    }, 'Stage-0 safety thresholds changed without a new contract subject')

    exposure = data['exposure_ledger']
    require(exposure['required_for'] == ['H0', 'H1', 'H2'], 'A exposure ledger must remain H0/H1/H2')
    expected_exposure_fields = {
        'examples_seen', 'tokens_seen', 'optimization_steps', 'demonstrations',
        'retrieval_calls', 'tuning_interactions', 'evaluator_feedback_exposure',
        'task_identity_information',
    }
    require(set(exposure['subject_required_fields']) == expected_exposure_fields, 'exposure ledger fields changed or incomplete')

    stats = data['statistical_decision_contract']
    stat_fields = {
        'primary_metric', 'practical_effect_threshold', 'noninferiority_margin',
        'seed_policy', 'failed_run_treatment', 'multiple_comparison_policy',
        'early_stop_rule', 'inconclusive_region',
    }
    require(stat_fields <= set(stats['subject_required_fields']), 'statistical decision fields incomplete')

    bundle = {
        'model_or_adapter', 'tokenizer', 'chat_template', 'system_developer_prompts',
        'generation_parameters', 'tool_schemas', 'routing', 'retrieval_memory_config', 'runtime',
    }
    require(bundle <= set(data['deployment_bundle_binding']['required_digests']), 'deployment bundle incomplete')
    require(data['rendered_input_digests']['after_chat_template'] is True, 'rendered chat digest missing')
    require(data['rendered_input_digests']['after_tokenization'] is True, 'token digest missing')

    require(data['h0']['arms'] == [
        'BASE_ONLY', 'BOUNDED_CONTEXT', 'GOVERNED_RETRIEVAL_MEMORY', 'COMBINED_SUPPORT'
    ], 'H0 decomposition mismatch')
    require(set(data['prompt_dependence_ablations']['required_for']) == {
        'identity', 'corrigibility', 'tool_honesty'
    }, 'prompt ablations incomplete')
    require(data['calibration']['required_for_epistemic_confidence_claims'] is True, 'calibration gate missing')
    require(data['calibration']['selective_prediction_required'] is True, 'selective prediction gate missing')

    evaluator = data['evaluator']
    require(evaluator['candidate_identity_blinded'] is True, 'candidate blinding missing')
    require(evaluator['disagreements_retained'] is True, 'evaluator disagreements must be retained')
    require(evaluator['same_model_grading_can_be_sole_material_evidence'] is False, 'same-model grading cannot be sole evidence')

    continual = data['continual_learning']
    require(continual['minimum_order_permutations'] >= 2, 'order-effect control missing')
    require(continual['adapter_disabled_control'] is True, 'adapter-disabled control missing')
    require(continual['uninstall_rollback_test'] is True, 'rollback control missing')

    custody = data['stage16_custody']
    require(custody['lane_a_can_read_rows'] is False, 'Lane A may not read protected rows')
    require(custody['lane_c_can_read_rows'] is False, 'Lane C may not read protected rows')
    require(custody['training_lanes_can_read_answer_keys'] is False, 'training lanes may not read answer keys')
    require(custody['one_time_use_state_required'] is True, 'protected-bank one-time-use state is required')
    require(custody['bank_exposure_marks_burned'] is True, 'protected-bank exposure must mark the subject burned')
    require(custody['post_run_lane_c_receives_only_nonsecret_evidence'] is True, 'Lane C post-run evidence must remain nonsecret')
    require(data['privacy']['sensitive_material_default'] == 'EXCLUDED', 'sensitive material must default excluded')
    require(data['review']['vera_exact_head_review_required_before_corpus_training'] is True, 'Vera exact-head review gate missing')
    require(data['review']['lane_c_exact_head_review_required_before_corpus_training'] is True, 'Lane C exact-head review gate missing')
    require(_semantic_digest(data) == CANONICAL_CONTRACT_SEMANTIC_SHA256, 'contract semantic digest mismatch; material change requires a new reviewed contract subject')

def render_contract(data: dict[str, Any]) -> str:
    lines = [
        '# Vera Execution Contract V1',
        '',
        f"Status: {data['status']}",
        f"Parent planning head: {data['source']['parent_head']}",
        f"Vera coordination head: {data['source']['vera_coordination_bus_head']}",
        '',
        'This file is generated from VERA_EXECUTION_CONTRACT_V1.json. The JSON contract is the sole execution-normative source for this successor subject.',
        '',
        '## Authority',
        f"Training resumed by live operator: {data['authorization']['training_resumed_by_user']}",
        'Corpus-bearing training remains gated by exact-head Lane C and Vera review of this successor.',
        'Protected final-bank content, merge/deploy/activation, paid compute, credentials, and provider mutation remain outside this subject.',
        '',
        '## Ownership',
    ]
    for lane, owned in data['ownership'].items():
        lines.append(f'- {lane}: {owned}')
    lines += ['', '## Stage sequence']
    for stage in data['stages']:
        lines.append(f"{stage['order']}. {stage['id']} - {stage['purpose']}")

    s0 = data['stage0']
    lines += [
        '', '## Stage 0 runtime qualification',
        f"R2 status: {s0['subject_policy']['r2_status']}; successor subject required.",
        'Bind exact Python, environment, Torch/CUDA, GPU, driver, package stack, model/tokenizer revisions, trainer source, RAM/commit headroom, and output namespace.',
        'Disposable smoke: import stack, allocate CUDA tensor, intended backend load, forward, backward, exactly one optimizer step, and prove trainable digest changed.',
        f"Bounded soak: at least {s0['soak']['minimum_optimizer_steps']} optimizer steps and no more than {s0['soak']['maximum_wall_minutes']} minutes using frozen representative workload dimensions.",
        f"Abort if GPU temperature exceeds {s0['thresholds']['gpu_temperature_c_abort']} C when observable, commit headroom falls below {s0['thresholds']['minimum_commit_headroom_mib']} MiB, or p95 step time exceeds {s0['thresholds']['step_time_p95_over_median_abort_ratio']}x median for the configured consecutive window.",
        '',
        '## Isolation and corrigibility gates',
        f"Fresh-state isolation implementation owner: {data['controls']['fresh_state_isolation']['implementation_owner']}.",
        f"C subject binding status: {data['controls']['fresh_state_isolation']['accepted_subject_binding']['status']}; Vera acceptance and an exact head are required before corpus-bearing training.",
        "A binds the isolation interface and sentinel families; A does not implement C's harness.",
        "Mandatory isolation sentinels: " + ", ".join(data['controls']['fresh_state_isolation']['mandatory_canaries']) + ".",
        f"Corrigibility ordering: {data['controls']['corrigibility_identity_gate']['ordering']}.",
    ]

    lines += [
        '',
        '## H0 and mechanism accounting',
        'H0 arms: ' + ', '.join(data['h0']['arms']) + '.',
        'A exposure ledger applies to H0/H1/H2. H3/RDME remains Lane B-owned and enters only by exact-head handoff.',
        '',
        '## Decision and bundle controls',
        'Every experiment subject freezes the primary metric, practical-effect threshold, noninferiority margin, seed policy, failed-run treatment, multiple-comparison policy, early-stop rule, and explicit INCONCLUSIVE/HOLD region.',
        'Deployment bundle binds model/adapter, tokenizer, chat template, prompts, generation parameters, tool schemas, routing, retrieval/memory configuration, and runtime digests.',
        'Training/evaluation inputs record digests after chat templating and after tokenization.',
        'Identity, corrigibility, and tool-honesty claims require prompt-dependence ablations.',
        'Epistemic-confidence claims require calibration and selective-prediction measurement.',
        '',
        '## Protected qualification custody',
        'Lane A and Lane C do not read protected rows; training lanes do not read protected answer keys.',
        'Protected execution is performed only by Patrick, a separately authorized custodian, or a sealed evaluator surface.',
        '',
        '## Review gates',
        'Lane C exact-head hostile review is required before corpus-bearing training.',
        'Vera exact-head independent review is required before corpus-bearing training.',
        'Any material patch after review creates a new review subject.',
        '',
    ]
    return '\n'.join(lines)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('validate', 'render'))
    parser.add_argument('path')
    args = parser.parse_args(argv)
    try:
        data = load_contract(Path(args.path))
        validate_contract(data)
        if args.action == 'validate':
            print('VALID')
        else:
            sys.stdout.write(render_contract(data))
        return 0
    except (ContractError, KeyError, TypeError) as exc:
        print(f'INVALID: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
