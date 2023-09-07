from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import subprocess
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__, level='DEBUG')

class M3U8Downloader:
    def __init__(self, out_dir=".", ffmpeg_log_dir=None,
                 http_proxy=None, max_parallel_workers=1, log=logger) -> None:
        """Initialize the downloader with configuration.

        Args:
            out_dir (str, optional): Directory for downloaded video files. Defaults to ".".
            ffmpeg_log_dir (str, optional): Path to directory for FFmpeg log. 
                Defaults to None for not dumping FFmpeg log.
            http_proxy (tuple, optional): String tuple of (ip address, port). 
                Defaults to None (use no proxy).
            max_parallel_workers: Max number of downloading tasks executed in parallel.
                Defaults to 1.
            log (_type_, optional): The terminal logger for the downloader. Defaults to logger.
        """
        self.log = log
        
        # Output directory.
        self._out_dir = Path(out_dir)
        if not self._out_dir.exists() or not self._out_dir.is_dir():
            self._out_dir.mkdir()
            self.log.info(f'Created {self._out_dir} as the output directory.')
        
        # FFmpeg log directory.
        if ffmpeg_log_dir is not None:
            self._ffmpeg_log_dir = Path(ffmpeg_log_dir)
            if not self._ffmpeg_log_dir.exists() or not self._ffmpeg_log_dir.is_dir():
                self._ffmpeg_log_dir.mkdir()
                self.log.info(f'Created {self._ffmpeg_log_dir} as the ffmpeg log directory.')
        else:
            self._ffmpeg_log_dir = None
        
        # Parallel.
        self._executor = ThreadPoolExecutor(max_workers=max_parallel_workers)
        self.log.info(f'The maximum number of parallel downloading is set to {max_parallel_workers}')

        # Proxy settings.
        if http_proxy is not None: 
            proxy_ip, proxy_port = http_proxy
            addr_http_proxy = f'http://{proxy_ip}:{proxy_port}/'
            self._sarg_http_proxy = f'-http_proxy {addr_http_proxy}'
        else:
            self._sarg_http_proxy = ''
        
    def __del__(self):
        self.wait_and_shutdown()
        self.log.info('Finished running. Destruct downloader.')
    
    def download(self, m3u8: str, filename: str):
        """Download a video designated by the given m3u8 file.

        Args:
            m3u8 (str): Path or hyperlink to the m3u8 file.
            filename (str): The output filename (with filetype suffix) of the downloaded video.
                e.g. "video.mp4"

        Returns:
            None
        """ 
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                
        # Output file path. Skip if the name already exists.
        out_path = self._out_dir/Path(filename)
        if out_path.exists():
            self.log.warning(f"Skip duplicated name [{filename}].")
            return
        
        # Build up the command line.
        sarg_m3u8 = f"-i {m3u8}"
        cmd = f'ffmpeg {self._sarg_http_proxy} {sarg_m3u8} -c copy {out_path}'
        
        if self._ffmpeg_log_dir is not None:
            ffmpeg_log_filename = f'{timestamp}-{filename}.log'
            ffmpeg_log_path = self._ffmpeg_log_dir / ffmpeg_log_filename
            cmd += f' > "{ffmpeg_log_path}" 2>&1' # Combine the output and error stream and dump it as a file.
        else:
            ffmpeg_log_path = None
        
        self._executor.submit(self._execute, cmd, task_title=filename, diag_file_path=ffmpeg_log_path)
        self.log.info(f'Submitted task [{filename}]')
        
            
    def _execute(self, cmd, task_title, diag_file_path):
        """Execute the given downloading command. 
        
        This method will be submitted to the executor for pending.

        Args:
            cmd (str): The ffmpeg command to be executed.
            task_title (str): Name to refer the submitted downloading task. Can be the downloaded file name.
            diag_file_path (str): Path of the diagnostic log file for reference if task fails.
                Can be the FFmpeg log file path.

        Returns:
            _type_: _description_
        """
        self.log.debug(f'Running cmd [{cmd}]...')
        t_begin = datetime.now()
        p = subprocess.run(cmd, shell=True)
        duration = datetime.now() - t_begin
            
        if p.returncode == 0: 
            self.log.info(f'Successed [{task_title}]. ({duration} used)')
        else: # The ffmpeg hasn't exited normally
            self.log.error(f'FFmpeg did NOT return properly.' +
                           (f' Log dumped to {diag_file_path}' if diag_file_path else ''))
            
    def wait_and_shutdown(self):
        self._executor.shutdown()

if __name__ == '__main__':
    proxy_config = ("127.0.0.1", "10809")
    out_dir = "./downloads"
    dlr = M3U8Downloader(out_dir, http_proxy=proxy_config)