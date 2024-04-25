import os
import time
from pathlib import Path
from threading import Timer


class OutdatedImageControl:
    def __init__(self, delete_folder_save: str | Path = "./downloaded_images", delete_folder_result: str | Path = "./results_images") -> None:
        self.delete_folder_save: Path = Path(delete_folder_save)
        self.delete_folder_result: Path = Path(delete_folder_result)
        self.remove_old_files(self.delete_folder_save, 60 * 5, 60e9 * 10)
        self.remove_old_files(self.delete_folder_result, 60 * 5, 60e9 * 10)

    def remove_old_files(self, folder: Path, check_interval: int = 60, time_diff_ns: int = 120e9):
        now = time.time_ns()
        for file in os.listdir(folder):
            path = Path.joinpath(folder, file)
            atime = os.stat(path).st_atime_ns
            if now - atime >= time_diff_ns:
                os.remove(path)

        Timer(check_interval, self.remove_old_files,
              [folder, check_interval, time_diff_ns]).start()
