import logging
import os
import tempfile
import ffmpeg

logger = logging.getLogger(__name__)


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
            crf=18,  # Set quality to 18
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
