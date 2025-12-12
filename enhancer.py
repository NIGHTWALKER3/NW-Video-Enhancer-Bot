import os
import tempfile
import ffmpeg
from realesrgan import RealESRGAN
from PIL import Image
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

model = RealESRGAN(device, scale=4)
model.load_weights("https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5/RealESRGAN_x4.pth", download=True)

def enhance_video(input_path, mode):
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    frames_dir = tempfile.mkdtemp()

    (
        ffmpeg
        .input(input_path)
        .output(f"{frames_dir}/frame_%04d.png", format="image2", vcodec="png")
        .overwrite_output()
        .run()
    )

    frame_files = sorted(os.listdir(frames_dir))
    enhanced_frames = tempfile.mkdtemp()

    for frame in frame_files:
        img = Image.open(os.path.join(frames_dir, frame))
        sr_image = model.predict(img)
        sr_image.save(os.path.join(enhanced_frames, frame))

    (
        ffmpeg
        .input(f"{enhanced_frames}/frame_%04d.png", framerate=30)
        .output(temp_output, vcodec="libx264", pix_fmt="yuv420p")
        .overwrite_output()
        .run()
    )

    return temp_output