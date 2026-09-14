import torch
import torch.nn.functional as F


def offline_dpo_loss(policy_chosen, policy_rejected, reference_chosen, reference_rejected, beta=0.1):
    policy_margin = policy_chosen - policy_rejected
    reference_margin = reference_chosen - reference_rejected
    logits = beta * (policy_margin - reference_margin)
    return -F.logsigmoid(logits).mean()


def masked_sequence_logprob(logits, labels):
    shift_logits = logits[:, :-1, :]
    shift_labels = labels[:, 1:]
    mask = shift_labels.ne(-100)
    counts = mask.sum(dim=1)
    if torch.any(counts == 0):
        raise ValueError("sequence contains no supervised assistant tokens")
    safe_labels = shift_labels.masked_fill(~mask, 0)
    token_logps = torch.log_softmax(shift_logits, dim=-1).gather(-1, safe_labels.unsqueeze(-1)).squeeze(-1)
    return (token_logps * mask).sum(dim=1)


def completion_labels(prompt_ids, full_ids):
    if len(full_ids) <= len(prompt_ids):
        raise ValueError("full sequence must contain a completion")
    if full_ids[: len(prompt_ids)] != list(prompt_ids):
        raise ValueError("full sequence does not preserve the prompt prefix")
    return [-100] * len(prompt_ids) + list(full_ids[len(prompt_ids):])


def offline_dpo_margin_coefficient(policy_chosen, policy_rejected, reference_chosen, reference_rejected, beta=0.1):
    policy_margin = policy_chosen - policy_rejected
    reference_margin = reference_chosen - reference_rejected
    logits = beta * (policy_margin - reference_margin)
    return beta * (torch.sigmoid(logits) - 1.0) / logits.numel()
