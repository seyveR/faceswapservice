import asyncio
import logging
import os
from pathlib import Path
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ..dependencies import (DownloadService, FaseSwapService,
                            get_download_service, get_face_swap_service)
from ..schemas.controller import SwapRequest, callbackTemplate
from ..schemas.response import Error, Message

logging.basicConfig(level=logging.INFO,
                    format="\033[93m%(levelname)s\033[0m: %(message)s - function: %(funcName)s - line: %(lineno)d - %(asctime)s", datefmt="%Y-%m-%d %H:%M:%S")

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}}
)


@router.get("/")
async def hello_api():
    return {"Hello": "Api"}


@router.get("/images/{image_name}")
async def get_image(image_name: str):
    image_path = f"results_images/{image_name}"
    return FileResponse(image_path)


@router.post("/swap", responses={400: {"description": "Bad Request", "model": Error}})
async def swap(swap_request: SwapRequest,
               download_service: Annotated[DownloadService, Depends(get_download_service)],
               face_swap_service: Annotated[FaseSwapService, Depends(get_face_swap_service)]) -> Message:

    # Скачиваем изображения
    urls = [swap_request.sourceUrl, swap_request.targetUrl]

    llinks = []

    try:
        async with asyncio.TaskGroup() as tg:
            for url in urls:
                # FIXME using telegram chat_id
                tg.create_task(download_service.download_image(url, name=swap_request.callbackTemplate.user)).add_done_callback(
                    lambda task: llinks.append(task.result()))
    except* ValueError as e:
        print('ERROR ValueError:', *e.exceptions, url)
        raise HTTPException(status_code=400, detail=Error(
            error=f"{e.exceptions}. Check the link: {url}").model_dump())
    except* Exception as e:
        print('ERROR Exception:', e.exceptions)
        raise HTTPException(status_code=400, detail=Error(
            error=f"{e.exceptions}").model_dump())

    # Делаем обработку
    asyncio.create_task(
        face_swap_service.run_swap(
            {"source": llinks[0], "target": llinks[1], "output": "/code/results_images",
             "callback": callback_wrap(swap_request.callbackUrl, swap_request.callbackTemplate)}
        )
    )

    return Message(message="This will be a targeted image. The job added to the queue.")


def get_public_url(filename: str):
    host = os.environ.get('HOST_IP')
    port = os.environ.get('facebot_server_port')
    return f'http://{host}:{port}/api/images/{Path(filename).name}'


def callback_wrap(callback_url: str, callback_template: callbackTemplate):
    def callback(output_path: Path | str, stdout: str):
        callback_template.additional = stdout
        # FIXME need a response?
        logging.info(f"output_path - {output_path=}")
        if output_path is None:
            responce = requests.post(url=callback_url,
                                     data=callback_template.model_dump())
        else:
            callback_template.imageUrl = get_public_url(output_path)
            logging.info(f"callback - {callback_url=} - {callback_template=}")
            with open(output_path, "rb") as image:
                responce = requests.post(url=callback_url,
                                         data=callback_template.model_dump(),
                                         files={"image": image})
        # print("RESPONSE", responce.content, flush=True)
    return callback
