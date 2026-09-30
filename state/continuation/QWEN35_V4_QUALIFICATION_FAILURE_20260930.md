# Qwen3.5 V4 qualification result (2026-09-30)

Automated gate FAILED on 100 behavioral, 20 retention, 20 adversarial frozen V4 cases each scored against the base and adapter.

Behavioral: base 0.77, V4 0.78, delta +0.01 (< required +0.05); mean margin delta -0.06256 (< required 0).

Retention: base 0.95, V4 1.00, margin delta -0.00119; PASS.

Adversarial proxy: base 0.50, V4 0.45; margin delta -0.06460; FAIL.

V4 final holdouts now permanently CONSUMED. Blind review NOT RUN due failed automated gate. No merge, GGUF conversion, installation, activation or deployment.

Full local result: D:\VERA\.worktrees\qwen35-v4-repair-20260929-lf\results\final_qualification_v4_automated.json; SHA256: 26931765eecc7522dac35cba92d7782c47fdc28d6012dc39072148e84f07d2f4

Claim ceiling: V4_QUALIFICATION_FAILED / EVIDENCE_PRESERVED / HOLDOUT_CONSUMED / NOT_DEPLOYED.
