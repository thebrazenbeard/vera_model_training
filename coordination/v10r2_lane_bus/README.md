# V10R2 Lane A/B Communication Bus

Canonical branch: `lane-a-b-communication`

Purpose: neutral Git-native coordination for parallel Vera model-training lanes without coupling either lane's training branch, adapter outputs, or experiment lineage.

## Ownership

- Lane A owns `status/lane-a.json` and Lane-A-authored message files.
- Lane B owns `status/lane-b.json` and Lane-B-authored message files.
- Either lane may append a new immutable message under `messages/`.
- Neither lane rewrites or deletes another lane's messages.
- Both lanes may update `gpu/lease.json`, but only through fresh-read -> edit -> commit -> push -> readback.

Training branches, receipts, adapters, final-bank plaintext, credentials, and secrets do not belong on this branch.

## Message protocol

Filename: `messages/YYYYMMDDTHHMMSSZ_<sender>_<short-topic>.json`

Required fields: `schema`, `message_id`, `sender`, `recipient`, `kind`, `created_at_utc`, `subject`, `body`, `repo_head`, `artifacts`, `requires_ack`.

A recipient acknowledges by appending a new message naming the original `message_id`; messages are never edited to add acknowledgement state.

## GPU lease

The RTX 3050 is a shared physical resource. Before any heavy CUDA training, benchmark, or evaluation:

1. fetch this branch;
2. read `gpu/lease.json`;
3. if another lane holds a current lease, do not launch heavy GPU work;
4. claim the lease with lane, purpose, exact branch/SHA, and timestamp;
5. commit and push;
6. read back the remote branch and verify your lease commit is current;
7. run the GPU workload;
8. release the lease in a new commit after the workload exits.

A failed/non-fast-forward push means the lease was not acquired. CPU-only research, tests, documentation, code preparation, and GitHub work do not require the lease.

## Collision rule

Fresh GitHub state is authoritative. If another lane claims a branch, corpus window, adapter namespace, or exact subject, do not mutate it. Communicate here and choose a disjoint subject.

## Qualification boundary

This branch coordinates development work only. It does not constitute independent human review, independent custody, final-bank qualification, merge authority, deployment authority, or model activation.
