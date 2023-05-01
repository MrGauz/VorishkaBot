import logging
import os
import tempfile
from asyncio import create_subprocess_exec
import ffmpeg

from settings import TGS_CONVERTER_PATH

logger = logging.getLogger(__name__)


async def convert_video(file_path: str) -> str | None:
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
            crf=18,  # Set quality to 18
            r=30,  # Set frame rate to 30 FPS
            an=None,  # Remove audio
            t=3,  # Limit the duration to 3 seconds
         )
         .run(capture_stdout=True, capture_stderr=True)
         )
    except ffmpeg.Error as e:
        logger.error(f'Failed to convert {file_path} with ffmpeg', e.stdout, e.stderr)
        return None

    os.remove(file_path)

    return webm_filename


async def convert_tgs(tgs_path: str) -> str | None:
    webm_filename = tempfile.mktemp(suffix='.webm')

    try:
        process = await create_subprocess_exec(TGS_CONVERTER_PATH, tgs_path, webm_filename)
        await process.wait()
    except OSError as e:
        logger.error(f'Failed to convert TGS {tgs_path}', e)
        return None

    if process.returncode != 0:
        logger.error(f'Failed to convert TGS {tgs_path}', process.stdout, process.stderr)
        return None

    os.remove(tgs_path)

    return webm_filename
