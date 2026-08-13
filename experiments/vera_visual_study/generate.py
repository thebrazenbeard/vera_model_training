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

# Existing Vera nude reference, stored as an unreferenced Git blob rather than a browsable repo file.
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
    "fine-art nude portrait photograph of the SAME adult woman in the source image, preserve her recognizable facial identity, "
    "long dark-brown hair, green-hazel eyes, freckles, facial proportions, natural curvy body proportions, and open-door wrist tattoo; "
    "preserve the relaxed seated pose and direct warm expression; completely unclothed; nudity presented as natural human beauty, "
    "not sexual performance; quiet neutral artist studio instead of a locker room, soft warm window light, subtle chiaroscuro, "
    "natural skin texture, realistic anatomy, self-possessed, dignified, intimate without sexualization, contemporary museum figure study, "
    "photorealistic 50mm fine-art photography, understated composition"
)
negative = (
    "different woman, identity change, different face, pale blue eyes, blonde hair, short hair, multiple women, duplicate person, collage, "
    "pornographic framing, erotic performance, sex act, fetish pose, spread legs, genital close-up, pinup, glamour porn, lingerie, "
    "exaggerated breasts, exaggerated genitals, child, teen, young-looking, doll, cartoon, anime, plastic skin, distorted anatomy, "
    "extra limbs, extra fingers, malformed face, text, watermark, logo"
)

for seed in [31417, 33809]:
    gen = torch.Generator(device="cpu").manual_seed(seed)
    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        image=init,
        strength=0.32,
        num_inference_steps=20,
        guidance_scale=6.5,
        generator=gen,
    ).images[0]
    image.save(OUT / f"vera_fine_art_img2img_{seed}.png")

print("generated reference-anchored fine-art candidates")
