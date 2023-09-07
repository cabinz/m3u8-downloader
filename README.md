It's an automation tool for m3u8 video downloading with MMmpeg.

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
dlr = M3U8Downloader(out_dir)

# Download a video.
dlr.download(m3u8, 'output_filename.mp4')
dlr.wait_and_shut_down()
```
If there is an existing file with the same name as specified, the task will be skipped.

## Proxy 
Use it with local http proxy:
```python3
proxy_config = ("127.0.0.1", "10809")
dlr = M3U8Downloader(out_dir, http_proxy=proxy_config)
```

## Diagnostics
Dump FFmpeg log to see why some downloads failed:
```python3
ffmpeg_log_dir = './ffmpeg_log'
dlr = M3U8Downloader(out_dir, ffmpeg_log_dir=ffmpeg_log_dir)
```

## Parallelism
Set the maximum parallel number of tasks (default as 1):
```python3
N = 3 # Set to 3 for example
dlr = M3U8Downloader(out_dir, max_parallel_workers=N)

tasks = [
    ('0.m3u8', '0.mp4'),
    ('1.m3u8', '1.mp4'),
    ('2.m3u8', '2.mp4'),
    ('3.m3u8', '3.mp4'),
    # ...
]

for m3u8, out_filename in tasks:
    dlr.download(m3u8, out_filename)
dlr.wait_and_shut_down()
```

All tasks specified to be downloaded will first be submitted to the executor and wait until there is an available executing quota.