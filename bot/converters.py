import io
import logging
import os
import tempfile

import ffmpeg
from PIL import Image

logger = logging.getLogger(__name__)


def convert_image(image: bytes) -> bytes:
    # Open image
    image = Image.open(io.BytesIO(image))
    width, height = image.size

    # Quantize the image to 8 bits (256 colors)
    image = image.quantize(colors=256, method=2)

    # Resize the image by scaling
    scale = 512 / max(width, height)
    new_width = 512 if width > height else int(width * scale)
    new_height = 512 if width < height else int(height * scale)
    image = image.resize((new_width, new_height), resample=Image.LANCZOS)

    # Save image to bytes
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='PNG')

    return output_buffer.getvalue()


def convert_video(file_path: str) -> str | None:
    webm_filename = tempfile.mktemp(suffix='.webm')

    # Get video metadata
    probe = ffmpeg.probe(file_path)
    video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    width = video_info['width']
    height = video_info['height']

    # Calculate new dimensions, keeping aspect ratio and satisfying the size constraint
    new_width = 512 if width >= height else int(width * (512 / height))
    new_height = 512 if width < height else int(height * (512 / width))

    try:
        (ffmpeg
         .input(file_path)
         .filter('scale', new_width, new_height)  # Resize the video
         .filter('loop', '30*3', '0')  # Loop the video for optimal user experience
         .output(
            webm_filename,
            format='webm',
            vcodec='libvpx-vp9',  # VP9 codec
            crf=30,  # Set quality to 30
            r=30,  # Set frame rate to 30 FPS
            an=None,  # Remove audio
            t=3,  # Limit the duration to 3 seconds
        )
         .run(capture_stdout=True, capture_stderr=True)
         )
    except ffmpeg.Error as e:
        logger.error(f'Failed to process {file_path}', e.stderr)
        return None

    os.remove(file_path)

    return webm_filename
