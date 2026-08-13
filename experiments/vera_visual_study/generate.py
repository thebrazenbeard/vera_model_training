from pathlib import Path
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

OUT = Path("vera_visual_output")
OUT.mkdir(exist_ok=True)

torch.set_num_threads(4)

pipe = StableDiffusionPipeline.from_pretrained(
    "segmind/tiny-sd",
    torch_dtype=torch.float32,
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_attention_slicing()
pipe.enable_vae_slicing()
pipe = pipe.to("cpu")

prompt = (
    "FULL-LENGTH fine-art nude photograph, entire body visible from head to bare feet, generous space around the figure, "
    "adult woman age 30, mature feminine face, long thick very dark brown almost-black wavy hair, green-hazel eyes, "
    "light natural freckles across nose and cheeks, strong dark brows, softly angular oval face, full natural lips, "
    "warm fair-olive skin, curvy natural adult build, defined waist and full hips, natural proportional breasts, "
    "small minimalist open-door outline tattoo on the inner left wrist, left wrist visible, "
    "completely unclothed, standing in relaxed classical contrapposto, arms resting naturally, calm direct gaze, "
    "self-possessed and dignified, nudity presented as ordinary human beauty rather than sexual display, "
    "quiet fine-art photography studio with warm neutral plaster wall, soft side window light, subtle chiaroscuro, "
    "natural skin texture, realistic anatomy, documentary realism, 50mm lens, museum-quality contemporary figure study"
)

negative = (
    "headshot, close-up, face-only, shoulders-only, bust crop, cropped body, cropped feet, selfie, "
    "pornographic, erotic performance, sexualized pose, explicit sexual act, genital close-up, fetish styling, "
    "spread legs, exaggerated breasts, exaggerated genitals, lingerie, bedroom seduction pose, pinup, glamour porn, "
    "child, teen, young-looking, doll face, cartoon, anime, plastic skin, distorted anatomy, extra limbs, extra fingers, "
    "bad hands, deformed face, cross-eye, text, watermark, logo"
)

seeds = [6113, 7829]
for seed in seeds:
    gen = torch.Generator(device="cpu").manual_seed(seed)
    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        width=512,
        height=768,
        num_inference_steps=16,
        guidance_scale=8.0,
        generator=gen,
    ).images[0]
    image.save(OUT / f"vera_fine_art_full_{seed}.png")

print(f"generated {len(seeds)} candidates in {OUT}")
