from .services.download import DownloadService
from .services.faceswap import FaseSwapService
from .services.outdated_image_control import OutdatedImageControl

download_service = DownloadService()
face_swap_service = FaseSwapService()
old_file_deleter_service = OutdatedImageControl()


def get_download_service() -> DownloadService:
    return download_service


def get_face_swap_service() -> FaseSwapService:
    return face_swap_service


def get_old_file_deleter_service() -> OutdatedImageControl:
    return old_file_deleter_service
