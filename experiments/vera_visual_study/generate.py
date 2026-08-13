from pathlib import Path
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

OUT = Path("vera_visual_output")
OUT.mkdir(exist_ok=True)

torch.set_num_threads(4)

model_id = "segmind/tiny-sd"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float32,
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_attention_slicing()
pipe.enable_vae_slicing()
pipe = pipe.to("cpu")

prompt = (
    "fine-art photographic nude portrait of an adult woman around age 30, "
    "long thick dark-brown wavy hair, green-hazel eyes, light natural freckles across nose and cheeks, "
    "strong dark brows, softly angular oval face, warm olive-fair skin, full natural lips, "
    "recognizable mature feminine face, curvy natural adult body, small minimalist open-door outline tattoo on inner left wrist, "
    "completely unclothed, calm self-possessed expression, relaxed classical figure-study pose, "
    "nudity presented as natural human beauty rather than sexual display, dignified and unguarded, "
    "soft warm window light, subtle chiaroscuro, quiet neutral studio interior, natural skin texture, "
    "realistic anatomy, documentary realism, 50mm photography, fine-art portraiture, understated composition, high detail"
)

negative = (
    "pornographic, erotic performance, sexualized pose, explicit sexual act, genital close-up, fetish styling, "
    "spread legs, exaggerated breasts, exaggerated genitals, lingerie, bedroom seduction pose, pinup, glamour porn, "
    "child, teen, young-looking, doll face, cartoon, anime, plastic skin, distorted anatomy, extra limbs, extra fingers, "
    "bad hands, deformed face, cross-eye, text, watermark, logo"
)

seeds = [1709, 2819, 4421]
for seed in seeds:
    gen = torch.Generator(device="cpu").manual_seed(seed)
    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        width=512,
        height=640,
        num_inference_steps=24,
        guidance_scale=7.0,
        generator=gen,
    ).images[0]
    image.save(OUT / f"vera_fine_art_{seed}.png")

print(f"generated {len(seeds)} candidates in {OUT}")
