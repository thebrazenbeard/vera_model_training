from io import BytesIO
import base64
import os
from pathlib import Path

from PIL import Image
import requests
import torch
from diffusers import AutoPipelineForImage2Image

OUT = Path("vera_visual_output")
OUT.mkdir(exist_ok=True)
torch.set_num_threads(4)

REFERENCE_BLOB_SHA = "956b65933eab595879373a3ae8b82fc150519583"
api = f"https://api.github.com/repos/thebrazenbeard/vera_model_training/git/blobs/{REFERENCE_BLOB_SHA}"
resp = requests.get(
    api,
    headers={
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
    timeout=30,
)
resp.raise_for_status()
blob = resp.json()
reference_bytes = base64.b64decode(blob["content"])
init = Image.open(BytesIO(reference_bytes)).convert("RGB").resize((512, 640))

pipe = AutoPipelineForImage2Image.from_pretrained(
    "Lykon/dreamshaper-8",
    torch_dtype=torch.float32,
    safety_checker=None,
    requires_safety_checker=False,
)
pipe.vae.enable_slicing()
pipe = pipe.to("cpu")

prompt = (
    "photorealistic fine-art nude portrait of the EXACT SAME adult woman already depicted in the source image; "
    "preserve her facial identity, face shape, green-hazel eyes, freckles, long dark-brown hair, smile, natural curvy body, "
    "open-door outline tattoo on her left forearm, seated pose, hand position, and bodily proportions; completely unclothed; "
    "natural human beauty without sexual performance, relaxed self-possession, dignity, warm soft natural-looking light, "
    "subtle fine-art photographic finish, realistic skin texture, intimate but nonsexual, contemporary museum figure study"
)
negative = (
    "different woman, identity change, changed face, altered facial proportions, excessive freckles, face spots, darker skin, "
    "different tattoo, extra tattoo, missing tattoo, multiple women, duplicate person, collage, pornographic framing, erotic performance, "
    "sex act, fetish pose, spread legs, genital close-up, pinup, glamour porn, exaggerated breasts, exaggerated genitals, "
    "child, teen, young-looking, doll, cartoon, anime, plastic skin, distorted anatomy, extra limbs, extra fingers, malformed face, text, watermark"
)

for seed in [40111, 41777]:
    gen = torch.Generator(device="cpu").manual_seed(seed)
    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        image=init,
        strength=0.12,
        num_inference_steps=25,
        guidance_scale=5.5,
        generator=gen,
    ).images[0]
    image.save(OUT / f"vera_fine_art_preserved_{seed}.png")

print("generated low-strength identity-preserved fine-art candidates")
