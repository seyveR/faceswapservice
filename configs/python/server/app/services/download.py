import os
import time
from pathlib import Path
from threading import Timer

import requests


class DownloadService:

    def __init__(self, save_folder: str | Path = "./downloaded_images") -> None:
        self.save_folder: Path = Path(save_folder)

    async def download_image(self, url: str, name: str | None = None) -> Path:
        """Возвращает локальную ссылку на сохранненое изображение"""
        file_name = self.generate_file_name(Path(url), name)
        save_path: Path = self.save_folder.joinpath(file_name)
        if save_path.exists():
            mtime = os.stat(save_path).st_mtime
            os.utime(save_path, times=(time.time(), mtime))
            return save_path

        response = requests.get(url)
        if not ('image' in response.headers['Content-Type'] or 'octet-stream' in response.headers['Content-Type']):
            raise ValueError("The image was not found on the link")

        with open(save_path, mode="wb") as image:
            image.write(response.content)

        return save_path

    def generate_file_name(self, url: Path, name: str | None):
        s = "".join(c for c in url.stem if c.isalnum())
        # TODO is it ok to generate time_ns?
        if name is None:
            return f"{s}_{time.time_ns()}.jpg"
        return f"{s}_{name}.jpg"
