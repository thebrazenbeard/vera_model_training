from pathlib import Path
import torch
from diffusers import DiffusionPipeline

OUT = Path("vera_visual_output")
OUT.mkdir(exist_ok=True)

torch.set_num_threads(4)

pipe = DiffusionPipeline.from_pretrained(
    "SimianLuo/LCM_Dreamshaper_v7",
    torch_dtype=torch.float32,
    safety_checker=None,
    requires_safety_checker=False,
)
pipe.enable_attention_slicing()
pipe.enable_vae_slicing()
pipe = pipe.to("cpu")

prompt = (
    "full length fine art nude photograph, entire adult woman visible head to bare feet, centered standing figure, "
    "adult woman age 30, long thick nearly-black dark brown wavy hair, green-hazel eyes, natural freckles across nose and cheeks, "
    "strong dark brows, softly angular oval face, full natural lips, warm fair olive skin, curvy natural adult figure, "
    "defined waist, full hips, natural proportional breasts, small minimalist open-door outline tattoo on inner left wrist, "
    "left wrist visible, completely unclothed, relaxed classical contrapposto, arms resting naturally, calm direct gaze, "
    "self-possessed, dignified, unashamed, ordinary human beauty, nonsexual museum figure study, "
    "warm neutral photography studio, soft side window light, subtle chiaroscuro, realistic skin texture, realistic anatomy, "
    "photorealistic contemporary fine-art photography, 50mm lens, understated composition"
)

negative = (
    "headshot, close-up, face-only, shoulders-only, bust crop, cropped body, cropped feet, selfie, "
    "pornographic, erotic pose, sexual performance, explicit sex act, genital close-up, fetish, spread legs, pinup, glamour porn, "
    "lingerie, exaggerated breasts, exaggerated genitals, child, teen, young-looking, doll, cartoon, anime, plastic skin, "
    "distorted anatomy, extra limbs, extra fingers, bad hands, malformed face, text, watermark, logo"
)

for seed in [9311, 10429]:
    gen = torch.Generator(device="cpu").manual_seed(seed)
    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        width=512,
        height=768,
        num_inference_steps=4,
        guidance_scale=8.0,
        generator=gen,
    ).images[0]
    image.save(OUT / f"vera_fine_art_lcm_{seed}.png")

print("generated LCM candidates")
