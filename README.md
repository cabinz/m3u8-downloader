Automation tool for m3u8 video download by MMmpeg.

# Dependencies

- python >= 3.8
- Download and install [FFmpeg](https://ffmpeg.org/) command line tool.

# Usage

```python3
from m3u8 import M3U8Downloader

# The existing output directory for you downloaded video files.
out_dir = '.'
# The link or path to the m3u8 file.
m3u8 = 'xxxxxx.m3u8'

# Initialize the downloader.
dlr = M3U8Downloader(out_dir, log=logger)

# Download a video.
dlr.download(m3u8, 'output_filename.mp4')
```

Use it with local http proxy:
```python3
proxy_config = ("127.0.0.1", "10809")
dlr = M3U8Downloader(out_dir, http_proxy=proxy_config)
```