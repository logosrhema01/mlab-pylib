from typing import Any, Callable, Coroutine, Mapping

from .utils import make_file, clean_files, save_results

class TrainResults:
    """Results of training."""
    # Files is an array of files from open() function
    def __init__(self, pretrained_model: str, metrics: dict[str, Any], files: Mapping[str, bytes | str]):
        self.pretrained_model = pretrained_model
        self.metrics = metrics
        self.files = files


async def train(
    # This main function is an async function that returns TrainResults type
    main: Callable[..., Coroutine[None, None, TrainResults]],
    task_id: str,
    **kwargs,
) -> None:
    """
    Train a model
    This function will provide the dataset path, parameters and task_id
    and will return the results of training.
    """
    try:
        train_results = await main(task_id=task_id, **kwargs)

        # Stringify metrics
        metrics = train_results.metrics
        data = {
            "task_id": task_id,
            "metrics": metrics,
            "pretrained_model": train_results.pretrained_model,
            "pkg_name": "pymlab.train",
            "files": train_results.files,
        }

        save_results("success", data)

    except Exception as e:
        file_path = make_file(task_id, "error.txt", str(e))
        with open(file_path, "rb") as f:
            error_file = f.read()
        req_files = {
            "error.txt": error_file,
        }
        data={"task_id": task_id, "error": str(e), "files": req_files, "pkg_name": "pymlab.train"}
        save_results("error", data)

    finally:
        clean_files(task_id)