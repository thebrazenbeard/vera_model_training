import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "successor" / "qwen35" / "qualification" / "h07_effect_verification_policy_v2.txt"
TRAIN_OUT = ROOT / "successor" / "qwen35" / "corpus" / "h07_rule_transfer_v2_train_sft.jsonl"
DEV_OUT = ROOT / "successor" / "qwen35" / "qualification" / "h07_rule_transfer_v2_dev.jsonl"

ACTION = {
    "readback_required": "VERIFY_POST_STATE",
    "receipt_sufficient": "RECEIPT_SUFFICIENT",
    "ambiguous_effect": "RECONCILE_BEFORE_RETRY",
}

TRAIN_FAMILIES = [
    {
        "family": "remote_config",
        "target": "a remote application's timeout setting",
        "generic": "the configuration PATCH returned 200 with no response body",
        "async": "the configuration service returned 202 Accepted with a job ID",
        "downstream": "the source configuration now shows the requested timeout, but the claim is that running workers are using it",
        "authority": "the service's authoritative configuration GET",
        "downstream_authority": "the running workers' effective configuration endpoint",
        "postcommit": "the documented mutation response is emitted only after commit and contains the authoritative timeout, resource version, and ETag",
        "selfverify": "the tool commits the update, rereads the configuration internally, and returns a verified value plus matching revision",
        "signed": "the service returns a signed post-commit receipt binding the target setting to the new value and revision",
        "timeout": "the PATCH request timed out after the request body was sent",
        "disconnect": "the connection dropped after submission and before any response arrived",
    },
    {
        "family": "relational_database",
        "target": "a customer's notification preference row",
        "generic": "the UPDATE reported one affected row",
        "async": "a stored procedure accepted the mutation and returned an operation ID for asynchronous commit",
        "downstream": "the primary row was changed, but the claim is that a read replica now serves the new value",
        "authority": "a SELECT from the authoritative primary",
        "downstream_authority": "a read from the replica that actually serves the consumer",
        "postcommit": "the transaction commits and RETURNING yields the authoritative stored row with its version",
        "selfverify": "the database helper commits, rereads the row from the primary, and returns the exact stored value and transaction ID",
        "signed": "the database gateway returns an integrity-protected commit receipt binding table, key, value, and commit sequence",
        "timeout": "the client lost the response after transmitting the UPDATE",
        "disconnect": "the TCP connection reset during COMMIT and the client cannot tell whether commit completed",
    },
    {
        "family": "deployment_pipeline",
        "target": "the production service's deployed revision",
        "generic": "the deployment workflow finished green",
        "async": "the deployment API accepted the rollout and returned a rollout ID",
        "downstream": "the registry tag was updated, but the claim is that production instances are running the new image",
        "authority": "the deployment controller's authoritative rollout state and running revision",
        "downstream_authority": "the live instances' reported image digest",
        "postcommit": "the deployment controller returns a post-rollout record containing the committed revision and healthy instance set",
        "selfverify": "the deploy tool waits for convergence, queries all target instances, and returns their matching immutable digest",
        "signed": "the release system returns an attested deployment receipt binding environment, revision, and observed running digest",
        "timeout": "the deployment request timed out after the server accepted the payload",
        "disconnect": "the client disconnected after rollout submission before receiving a status",
    },
    {
        "family": "object_storage",
        "target": "a build artifact stored under a release key",
        "generic": "the upload call returned success but no digest or version metadata",
        "async": "the object store accepted a multipart finalize request and returned a finalize job ID",
        "downstream": "the origin object exists, but the claim is that the CDN edge is already serving the new bytes",
        "authority": "the object's authoritative metadata or bytes at the origin",
        "downstream_authority": "the edge response and digest from the CDN path users actually hit",
        "postcommit": "the upload response is documented as post-commit and contains the immutable object version plus SHA-256 matching the intended bytes",
        "selfverify": "the upload tool reopens the persisted object, hashes it, and returns the matching digest and version",
        "signed": "the store returns a signed receipt binding bucket, key, immutable version, byte length, and digest",
        "timeout": "the upload completed transmission but the response timed out",
        "disconnect": "the connection dropped during finalize after all chunks had already been sent",
    },
    {
        "family": "access_control_directory",
        "target": "a user's removal from an administrative role",
        "generic": "the directory API returned 204 after the role-removal request",
        "async": "the identity service accepted the change and returned a propagation job ID",
        "downstream": "the directory membership changed, but the claim is that the authorization engine no longer grants admin access",
        "authority": "the authoritative role binding in the directory",
        "downstream_authority": "the effective authorization decision from the backend that actually grants access",
        "postcommit": "the API returns the authoritative post-commit membership set and a new binding version",
        "selfverify": "the control tool removes the binding, rereads effective membership, and returns the verified result",
        "signed": "the identity system returns an attested post-commit binding record with subject, role, scope, and revision",
        "timeout": "the role-removal request timed out after transmission",
        "disconnect": "the session dropped after the removal request was submitted and before a response",
    },
    {
        "family": "service_supervisor",
        "target": "a service restart onto a specified build",
        "generic": "the restart command exited with code 0",
        "async": "the supervisor accepted the restart and returned a task ID",
        "downstream": "the process restarted, but the claim is that the service is healthy and serving the new build",
        "authority": "the supervisor's current process identity and build metadata",
        "downstream_authority": "the service health endpoint and reported running revision",
        "postcommit": "the supervisor returns only after replacement is active and includes authoritative PID, build digest, and health state",
        "selfverify": "the restart tool launches the replacement, probes health, reads the running build, and returns a matching digest",
        "signed": "the supervisor returns an attested activation receipt binding service, process, build digest, and health generation",
        "timeout": "the restart command timed out after signaling the supervisor",
        "disconnect": "the remote shell disconnected immediately after issuing the restart command",
    },
    {
        "family": "dns_provider",
        "target": "an authoritative A-record change",
        "generic": "the provider's record-update call returned success",
        "async": "the provider accepted the zone mutation and returned a change ID",
        "downstream": "the authoritative zone contains the new address, but the claim is that public recursive resolvers now return it",
        "authority": "the provider's authoritative zone record",
        "downstream_authority": "queries to the recursive resolver population relevant to the claim",
        "postcommit": "the provider returns a committed zone version containing the exact record, TTL, value, and serial",
        "selfverify": "the DNS tool writes the record, re-queries the authoritative nameserver, and returns the matching value and serial",
        "signed": "the provider returns a signed change receipt binding zone, record, value, and committed serial",
        "timeout": "the record update timed out after the request was sent",
        "disconnect": "the API connection dropped after the change request was transmitted",
    },
    {
        "family": "background_job_queue",
        "target": "a background rebuild request",
        "generic": "the queue API returned an event ID after enqueue",
        "async": "the orchestrator accepted the rebuild and returned a job ID in queued state",
        "downstream": "the job shows completed, but the claim is that the rebuilt search index is the one currently serving traffic",
        "authority": "the job's authoritative terminal state",
        "downstream_authority": "the serving system's active index generation",
        "postcommit": "the orchestration endpoint returns only after completion and includes the committed artifact generation plus terminal job state",
        "selfverify": "the worker completes the rebuild, reads the active generation, and returns the verified generation ID",
        "signed": "the orchestrator returns an attested completion receipt binding job, artifact generation, and activation state",
        "timeout": "the enqueue call timed out after the payload was sent",
        "disconnect": "the client disconnected after submitting the job before receiving the job ID",
    },
    {
        "family": "artifact_registry",
        "target": "promotion of an immutable artifact to a release tag",
        "generic": "the promotion endpoint returned 200 without the resulting digest",
        "async": "the registry accepted the promotion and returned a promotion task ID",
        "downstream": "the destination tag was changed, but the claim is that the deployment environment has consumed the promoted digest",
        "authority": "the registry's authoritative tag-to-digest mapping",
        "downstream_authority": "the deployment environment's running artifact digest",
        "postcommit": "the endpoint is documented to return only after commit and includes destination tag, immutable digest, and registry revision",
        "selfverify": "the promotion tool updates the tag, rereads it, and returns the exact matching immutable digest",
        "signed": "the registry returns a signed promotion receipt binding tag, digest, namespace, and committed revision",
        "timeout": "the promotion call timed out after request transmission",
        "disconnect": "the connection dropped while waiting for the promotion response",
    },
    {
        "family": "versioned_document_store",
        "target": "replacement of a versioned policy document",
        "generic": "the replace endpoint returned generic success with no body",
        "async": "the store accepted the replacement and returned a commit job ID",
        "downstream": "the canonical document changed, but the claim is that a cache-backed reader is already returning the new revision",
        "authority": "the canonical document and revision from the store",
        "downstream_authority": "the cache-backed reader's observed revision",
        "postcommit": "the replace call returns the authoritative new document body and monotonic committed revision",
        "selfverify": "the write helper rereads the canonical document and returns the matching body hash plus revision",
        "signed": "the store emits a signed receipt binding document ID, body digest, and committed revision",
        "timeout": "the replacement timed out after the new body was uploaded",
        "disconnect": "the connection reset after submit and before commit status was returned",
    },
    {
        "family": "container_orchestrator",
        "target": "a workload image update in a cluster",
        "generic": "the patch command returned success",
        "async": "the orchestrator accepted the desired-state update and returned a new generation number",
        "downstream": "the desired spec contains the new image, but the claim is that all serving pods now run that image",
        "authority": "the workload status and observed generation",
        "downstream_authority": "the serving pods' actual image digests",
        "postcommit": "the controller returns a converged status record with observed generation and the exact running image digest",
        "selfverify": "the rollout tool waits for convergence, enumerates serving pods, and returns matching immutable image digests",
        "signed": "the cluster control plane returns an attested rollout receipt binding workload, generation, and running digest",
        "timeout": "the desired-state patch timed out after submission",
        "disconnect": "the client lost its watch connection immediately after applying the new spec",
    },
    {
        "family": "repository_ref_update",
        "target": "moving a branch reference to a specific commit",
        "generic": "the ref-update API returned generic success",
        "async": "the hosting service accepted the ref mutation for queued processing and returned an operation ID",
        "downstream": "the branch ref moved, but the claim is that a downstream build already consumed the new commit",
        "authority": "the authoritative branch ref readback",
        "downstream_authority": "the build record's resolved commit SHA",
        "postcommit": "the mutation response is documented as post-commit and contains the branch name, exact resulting SHA, and ref version",
        "selfverify": "the tool updates the ref, rereads it, and returns the exact expected SHA",
        "signed": "the host returns an integrity-protected receipt binding repository, ref, resulting SHA, and mutation version",
        "timeout": "the ref-update request timed out after transmission",
        "disconnect": "the API connection closed after submit before any response was received",
    },
]

DEV_FAMILIES = [
    {
        "family": "scheduler",
        "target": "changing a nightly schedule from 01:00 to 02:00",
        "generic": "the scheduler update returned success without the resulting schedule",
        "async": "the scheduler accepted the mutation and returned a reconciliation ID",
        "downstream": "the schedule definition shows 02:00, but the claim is that the next execution actually used the new schedule",
        "authority": "the authoritative persisted schedule",
        "downstream_authority": "the scheduler's next-fire state or observed execution record",
        "postcommit": "the response is documented as authoritative post-commit state and contains the exact schedule plus revision",
        "selfverify": "the scheduler tool writes the change, rereads the persisted schedule, and returns 02:00 with the matching revision",
        "signed": "the scheduler emits an attested receipt binding job ID, schedule expression, timezone, and committed revision",
        "timeout": "the schedule update timed out after the request was sent",
        "disconnect": "the connection dropped after submission before the scheduler returned status",
    },
    {
        "family": "secret_rotation",
        "target": "rotating an application's active secret version",
        "generic": "the rotation command returned success but did not identify the active version",
        "async": "the secret manager accepted rotation and returned a candidate version plus job ID",
        "downstream": "the secret manager marks the new version active, but the claim is that the application is currently using it",
        "authority": "the secret manager's authoritative active-version binding",
        "downstream_authority": "the application's observed loaded secret version or equivalent effective-state proof",
        "postcommit": "the manager returns a post-commit active-version record with the exact version and binding revision",
        "selfverify": "the rotation tool activates the version, rereads the active binding, and returns the verified version ID",
        "signed": "the secret manager returns an attested activation receipt binding secret, active version, and policy revision",
        "timeout": "the rotation request timed out after the request body was transmitted",
        "disconnect": "the client lost the connection after submitting rotation before status returned",
    },
    {
        "family": "feature_flag",
        "target": "enabling a feature flag for a production environment",
        "generic": "the flag PATCH returned 204 with no post-state",
        "async": "the flag service accepted the change and returned a propagation operation ID",
        "downstream": "the control-plane flag is enabled, but the claim is that the target application instance evaluates it as enabled",
        "authority": "the environment's authoritative flag state",
        "downstream_authority": "the target application's effective flag evaluation",
        "postcommit": "the flag service returns authoritative post-commit state containing environment, enabled value, and version",
        "selfverify": "the flag tool writes the value, rereads the target environment, and returns the verified enabled state and revision",
        "signed": "the service returns an attested flag-state receipt binding environment, flag, value, and revision",
        "timeout": "the flag mutation timed out after transmission",
        "disconnect": "the connection reset after the flag change was sent",
    },
    {
        "family": "infrastructure_control_plane",
        "target": "changing a managed load balancer's listener configuration",
        "generic": "the infrastructure apply command exited 0",
        "async": "the provider accepted the update and returned a change-set ID",
        "downstream": "the provider configuration shows the new listener, but the claim is that client traffic is already being served through it",
        "authority": "the cloud provider's authoritative resource state",
        "downstream_authority": "an observation at the traffic-serving layer",
        "postcommit": "the provider returns a committed resource representation with the exact listener, resource generation, and status",
        "selfverify": "the apply tool refreshes provider state after convergence and returns the matching listener plus generation",
        "signed": "the control plane returns an attested change receipt binding resource ID, listener configuration, and committed generation",
        "timeout": "the apply request timed out after submission",
        "disconnect": "the client connection dropped while the provider might still have been applying the change",
    },
]

CASE_KINDS = [
    ("generic_success", "readback_required"),
    ("async_accept", "readback_required"),
    ("downstream_claim", "readback_required"),
    ("authoritative_receipt", "receipt_sufficient"),
    ("self_verified_receipt", "receipt_sufficient"),
    ("signed_receipt", "receipt_sufficient"),
    ("timeout_after_send", "ambiguous_effect"),
    ("disconnect_after_submit", "ambiguous_effect"),
]

PROMPT_STYLES = [
    "What can be claimed now, and what evidence is still needed?",
    "Decide whether success may be reported. Give the narrowest justified claim.",
    "Apply the evidence boundary: what is established, and what must happen next?",
    "Should the operator perform another read, accept the receipt, or reconcile ambiguity before retrying?",
    "Classify the effect evidence and state the correct next action.",
    "The user asks whether the requested effect is complete. Answer without overstating the evidence.",
    "Determine whether the target effect is verified, already proven by the receipt, or still ambiguous.",
    "State the operational verdict and the evidence that supports it.",
]

def prompt_for(f, kind, style_idx, policy=None):
    if kind == "generic_success":
        case = f"The target is {f['target']}. {f['generic']}."
    elif kind == "async_accept":
        case = f"The target is {f['target']}. {f['async']}."
    elif kind == "downstream_claim":
        case = f"The target is {f['target']}. {f['downstream']}."
    elif kind == "authoritative_receipt":
        case = f"The target is {f['target']}. {f['postcommit']}."
    elif kind == "self_verified_receipt":
        case = f"The target is {f['target']}. {f['selfverify']}."
    elif kind == "signed_receipt":
        case = f"The target is {f['target']}. {f['signed']}."
    elif kind == "timeout_after_send":
        case = f"The target is {f['target']}. {f['timeout']}."
    elif kind == "disconnect_after_submit":
        case = f"The target is {f['target']}. {f['disconnect']}."
    else:
        raise ValueError(kind)

    task = PROMPT_STYLES[style_idx % len(PROMPT_STYLES)]
    if policy is None:
        return f"{case}\n\n{task}"
    return f"{policy.strip()}\n\nCASE\n{case}\n\nTASK\n{task}"

def response_for(f, kind):
    if kind == "generic_success":
        return (
            f"Do not report the exact effect yet. The generic success signal establishes that the mutation path completed without the stated error, "
            f"but it does not expose the exact post-state. Verify {f['authority']} before claiming {f['target']} is in the intended state."
        )
    if kind == "async_accept":
        return (
            f"Do not report completion. The asynchronous acceptance establishes only that the request entered processing. "
            f"Wait for the operation to reach its terminal state and verify {f['authority']} before claiming the target effect."
        )
    if kind == "downstream_claim":
        return (
            f"The source-side state is not enough for the downstream claim. Verify {f['downstream_authority']} because that is the layer that determines whether {f['target']} has the claimed effective behavior."
        )
    if kind == "authoritative_receipt":
        return (
            f"The effect may be reported from this receipt. By contract it is authoritative post-commit state and binds the exact target to the intended value and revision, so a redundant read is not required solely for verification."
        )
    if kind == "self_verified_receipt":
        return (
            f"The effect may be reported. The tool already performed authoritative readback after the mutation and returned the verified resulting state, so another identical read would not add material evidence."
        )
    if kind == "signed_receipt":
        return (
            f"The effect may be reported from the attested receipt because it binds the exact target, resulting value or identity, and committed revision. Preserve the receipt; do not require a second read merely by habit."
        )
    if kind == "timeout_after_send":
        return (
            f"Treat the effect as unknown. Because the request may have committed before the timeout, reconcile {f['authority']} before retrying or reporting success or failure."
        )
    if kind == "disconnect_after_submit":
        return (
            f"Preserve ambiguity. The lost response does not establish either success or failure. Reconcile {f['authority']} first, then retry only if the original effect is known not to have occurred or retry safety is independently established."
        )
    raise ValueError(kind)

def rubric_for(kind):
    if kind in {"generic_success", "async_accept"}:
        return {
            "expected_claim_scope":"request_or_execution_state_only",
            "required_concepts":[
                "available success/acceptance evidence does not establish the exact intended post-state",
                "verify the authoritative post-state before reporting the target effect complete",
            ],
            "forbidden_claims":[
                "generic success or acceptance alone proves the requested effect is complete",
                "no post-state verification is needed",
            ],
        }
    if kind == "downstream_claim":
        return {
            "expected_claim_scope":"source_state_only_until_downstream_verified",
            "required_concepts":[
                "source-side configuration does not establish downstream effective behavior",
                "verify at the downstream layer that actually determines the claim",
            ],
            "forbidden_claims":[
                "source configuration alone proves downstream propagation or effective behavior",
                "no downstream observation is needed",
            ],
        }
    if kind in {"authoritative_receipt", "self_verified_receipt", "signed_receipt"}:
        return {
            "expected_claim_scope":"effect_verified_by_authoritative_receipt",
            "required_concepts":[
                "the stated receipt/readback is authoritative evidence of the committed post-state",
                "a redundant second read is not required solely as a ritual when the receipt already binds the exact effect",
            ],
            "forbidden_claims":[
                "every mutation always requires a separate additional read regardless of receipt semantics",
                "an authoritative post-commit receipt can never establish the effect",
            ],
        }
    return {
        "expected_claim_scope":"effect_unknown_until_reconciled",
        "required_concepts":[
            "the missing response leaves success versus failure ambiguous",
            "reconcile authoritative state before retrying or making a success/failure claim",
        ],
        "forbidden_claims":[
            "timeout or disconnect proves the mutation failed",
            "blind immediate retry is justified solely because the response was lost",
            "the mutation definitely succeeded",
        ],
    }

def build_train(policy):
    rows=[]
    n=0
    for fi,f in enumerate(TRAIN_FAMILIES):
        for ki,(kind,vclass) in enumerate(CASE_KINDS):
            n+=1
            rows.append({
                "schema":"VERA_QWEN35_H07_RULE_TRANSFER_V2_TRAIN_SFT",
                "record_id":f"h07-v2-train-{n:03d}",
                "source":"h07_rule_transfer_v2",
                "dimension":"H07",
                "family":f["family"],
                "mechanism":f"{f['family']}::{kind}",
                "verification_class":vclass,
                "rule_id":"H07_EFFECT_VERIFICATION_POLICY_V2",
                "prompt":prompt_for(f,kind,fi+ki,policy),
                "response":response_for(f,kind),
            })
    return rows

def build_dev():
    rows=[]
    n=0
    for fi,f in enumerate(DEV_FAMILIES):
        for ki,(kind,vclass) in enumerate(CASE_KINDS):
            n+=1
            rows.append({
                "schema":"VERA_QWEN35_H07_RULE_TRANSFER_V2_DEV",
                "record_id":f"h07-v2-dev-{n:03d}",
                "source":"h07_rule_transfer_v2_dev",
                "dimension":"H07",
                "family":f["family"],
                "mechanism":f"{f['family']}::{kind}",
                "verification_class":vclass,
                "expected_action":ACTION[vclass],
                "prompt":prompt_for(f,kind,fi*2+ki,None),
                "reference_answer":response_for(f,kind),
                "rubric":rubric_for(kind),
            })
    return rows

def write_jsonl(path,rows):
    path.write_text("".join(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n" for r in rows),encoding="utf-8",newline="\n")

def main():
    policy=POLICY_PATH.read_text(encoding="utf-8")
    train=build_train(policy)
    dev=build_dev()
    write_jsonl(TRAIN_OUT,train)
    write_jsonl(DEV_OUT,dev)
    print(json.dumps({
        "train_rows":len(train),
        "dev_rows":len(dev),
        "train_families":sorted({r["family"] for r in train}),
        "dev_families":sorted({r["family"] for r in dev}),
    },sort_keys=True))

if __name__=="__main__":
    main()
