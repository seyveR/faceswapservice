import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from torch import cuda


@dataclass()
class FaceSwapArguments:
    source: Path
    target: Path
    output: Path | str
    processor: bool | None = True
    callback: Callable | None = None
    cuda: bool | None = False

    def __str__(self) -> str:
        s = ""
        if self.processor:
            s += " --frame-processor face_swapper face_enhancer"
        if self.cuda:
            s += " --execution-provider cuda"
        s += f" --source {self.source}"
        s += f" --target {self.target}"
        s += f" --output {self.output}"
        return s


class FaseSwapService:
    def __init__(self, face_swap_root: str | Path = "./results_images") -> None:
        self.fase_swap_root = face_swap_root
        self.max_workers = int(os.environ.get('MAX_JOBS'))
        self.semaphore = asyncio.Semaphore(self.max_workers)
        self.cuda = cuda.is_available()

    async def run_swap(self, arguments: dict | FaceSwapArguments) -> None:
        """Запускает roop модель и сохраняет результат"""
        arguments = FaceSwapArguments(**arguments)
        output: Path = Path.joinpath(Path(arguments.output),
                                     self.generate_name(arguments.source, arguments.target))

        if output.exists():
            arguments.callback(output_path=output,
                               stdout="Данная пара изображений уже обработана")
            return

        arguments.output = output
        # arguments.cuda = True

        async with self.semaphore:
            process = await asyncio.create_subprocess_shell(f"python roop/run.py {arguments}",
                                                            stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)

            stdout, stderr = await process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()

            # FIXME downloading weights?
            if stderr != "":
                if "[00:00<" in stderr:
                    print("Model loaded")
                elif "NNPACK" in stderr:
                    print("NO NNPACK")
                else:
                    print("stderr", stderr, flush=True)
                    arguments.callback(output_path=None, stdout=stderr)
                    # raise Exception(stderr)
                    return

            # This method does not raise any Exception because it is assumed that it is nested in asyncio.create_task()
            if 'No face in source path detected.' in stdout:
                arguments.callback(
                    output_path=None, stdout="Не найдено лицо для перемещения")
                logging.info(
                    f"No face in source path detected source={arguments.source}")
                # raise Exception("No face in source path detected.")
                return

            if "Processing to image succeed!" not in stdout:
                arguments.callback(
                    output_path=None, stdout="Данные изображения невозможно обработать")
                logging.info(
                    f"Failed to processe images source={arguments.source} target={arguments.target}")
                # raise Exception("Faild to processe images!")
                return

            arguments.callback(output_path=output, stdout=stdout)

    def generate_name(self, source: Path, target: Path) -> Path:
        return Path(f"{source.stem}_{target.stem}.jpg")
