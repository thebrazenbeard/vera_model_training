from pathlib import Path
from PIL import Image
import torch
from diffusers import AutoPipelineForText2Image, LCMScheduler

OUT = Path("vera_visual_output")
OUT.mkdir(exist_ok=True)
torch.set_num_threads(4)

pipe = AutoPipelineForText2Image.from_pretrained(
    "Lykon/dreamshaper-8",
    torch_dtype=torch.float32,
    safety_checker=None,
    requires_safety_checker=False,
)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5")
pipe.fuse_lora()
pipe.load_ip_adapter(
    "h94/IP-Adapter",
    subfolder="models",
    weight_name="ip-adapter-plus-face_sd15.safetensors",
)
pipe.set_ip_adapter_scale(0.45)
pipe.vae.enable_slicing()
pipe = pipe.to("cpu")

ref = Image.open(
    "experiments/vera_visual_study/reference/vera_face_verified_128.jpg"
).convert("RGB")

prompt = (
    "ONE WOMAN ONLY, single subject, full-length fine-art nude photograph, one adult woman visible from head to bare feet, "
    "same adult woman's facial identity and recognizable face as the reference portrait, age 30, long thick dark-brown wavy hair, "
    "green-hazel eyes, natural freckles across nose and cheeks, strong dark brows, softly angular oval face, full natural lips, "
    "warm fair-olive skin, curvy natural adult figure, defined waist, full hips, natural proportional breasts, "
    "small minimalist open-door outline tattoo on inner left wrist, left wrist visible, completely unclothed, "
    "relaxed classical contrapposto, arms resting naturally, calm direct gaze, self-possessed and dignified, "
    "nudity presented as ordinary human beauty rather than sexual display, contemporary museum figure study, "
    "quiet warm neutral studio, soft side window light, subtle chiaroscuro, natural skin texture, realistic anatomy, "
    "photorealistic 50mm fine-art portrait photography, understated composition, no props"
)

negative = (
    "multiple women, two women, twins, duplicate person, duplicate figure, extra person, collage, split screen, contact sheet, "
    "floating faces, background portraits, headshot, close-up, cropped body, cropped feet, selfie, "
    "pornographic, erotic pose, sexual performance, sex act, genital close-up, fetish, spread legs, pinup, glamour porn, "
    "lingerie, exaggerated breasts, exaggerated genitals, child, teen, young-looking, doll, cartoon, anime, plastic skin, "
    "distorted anatomy, extra limbs, extra fingers, bad hands, malformed face, text, watermark, logo"
)

for seed in [20531, 23627]:
    gen = torch.Generator(device="cpu").manual_seed(seed)
    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        ip_adapter_image=ref,
        width=512,
        height=768,
        num_inference_steps=6,
        guidance_scale=1.5,
        generator=gen,
    ).images[0]
    image.save(OUT / f"vera_fine_art_dreamshaper_{seed}.png")

print("generated single-subject identity-conditioned candidates")
