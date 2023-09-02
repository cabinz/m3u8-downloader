from datetime import datetime
import subprocess
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

class M3U8Downloader:
    def __init__(self, out_dir=".", http_proxy=None, log=logger) -> None:
        """Initialize the downloader with configuration.

        Args:
            out_dir (str, optional): Directory for downloaded video files. Defaults to ".".
            http_proxy (tuple, optional): String tuple of (ip address, port). 
                Defaults to None (use no proxy).
            log (_type_, optional): The terminal logger for the downloader. Defaults to logger.
        """
        self.log = log
        
        # output directory
        self.__out_dir = Path(out_dir)
        if not self.__out_dir.exists() or not self.__out_dir.is_dir():
            self.__out_dir.mkdir()
            self.log.info(f'Created {self.__out_dir} as the output directory.')

        # proxy setting
        if http_proxy is not None: 
            proxy_ip, proxy_port = http_proxy
            addr_http_proxy = f'http://{proxy_ip}:{proxy_port}/'
            self.__sarg_http_proxy = f'-http_proxy {addr_http_proxy}'
        else:
            self.__sarg_http_proxy = ''
    
    def download(self, m3u8: str, filename: str, ffmpeg_log_dir: str = 'ffmpeg_log'):
        """Download a video designated by the given m3u8 file.

        Args:
            m3u8 (str): Path or hyperlink to the m3u8 file.
            filename (str): The output filename (with filetype suffix) of the downloaded video.
                e.g. "video.mp4"
            ffmpeg_log_dir (str, optional): The ffmpeg log directory. Defaults to 'ffmpeg_log'.

        Returns:
            None
        """ 
        # output file path
        out_path = self.__out_dir/Path(filename)
        if (out_path.exists()):
            self.log.info(f"Skip duplicated name [{filename}].")
            return
        
        # ffmpeg log dump
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        ffmpeg_log_dir = Path(ffmpeg_log_dir)
        if not ffmpeg_log_dir.exists() or not ffmpeg_log_dir.is_dir():
            ffmpeg_log_dir.mkdir()
            self.log.info(f'Created {ffmpeg_log_dir} as the ffmpeg log dump directory.')
        log_path = ffmpeg_log_dir / f'{timestamp}-{filename}.log'
        
        # m3u8 setting
        sarg_m3u8 = f"-i {m3u8}"
        # run
        cmd = f'ffmpeg {self.__sarg_http_proxy} {sarg_m3u8} -c copy {out_path}'
        with log_path.open('w+t') as f_log:
            t_begin = datetime.now()
            try:
                self.log.info(f'Task [{filename}]')
                p = subprocess.run(
                    cmd.split(),
                    stdout=f_log,
                    stderr=f_log
                )
            except Exception as e:
                self.log.error(f'Script exception: {e}')
            duration = datetime.now() - t_begin
            if p.returncode == 0: 
                self.log.info(f'Successed. ({duration} used)')
            else: # The ffmpeg hasn't exited normally
                self.log.error(f'ffmpeg did NOT return properly. Log dumped to {log_path}')
            

if __name__ == '__main__':
    proxy_config = ("127.0.0.1", "10809")
    out_dir = "./download"
    dlr = M3U8Downloader(out_dir, http_proxy=proxy_config)