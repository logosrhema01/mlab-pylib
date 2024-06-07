"""
Do not edit this file
This is the file that will be used to train your model
"""
import os
import json
import requests
from typing import Callable, Coroutine, Mapping

class TrainResults:
    """Results of training."""
    # Files is an array of files from open() function
    def __init__(self, pretrained_model: str, metrics: dict[str, float], files: Mapping[str, bytes | str]):
        self.pretrained_model = pretrained_model
        self.metrics = metrics
        self.files = files


async def train(
    # This main function is an async function that returns TrainResults type
    main: Callable[..., Coroutine[None, None, TrainResults]],
    result_id: str,
    api_url: str,
    user_token: str,
    **kwargs,
) -> None:
    """
    Train a model
    This function will provide the dataset path, parameters and result_id
    and will return the results of training.
    """
    try:
        train_results = await main(result_id=result_id, **kwargs)

        # Stringify metrics
        metrics = json.dumps(train_results.metrics)
        data = {
            "result_id": result_id,
            "metrics": metrics,
            "pretrained_model": train_results.pretrained_model,
            "pkg_name": "pymlab.train",
        }

        response = requests.post(api_url, data=data, files=train_results.files,timeout=120, verify=False, headers={"Authorization":user_token})

        if response.status_code == 200:
            # delete files
            for file in train_results.files.items():
                os.remove(file[0])
        else:
            raise requests.HTTPError(f"Error uploading results. Status code: {response.status_code}, error: {response.text}")

    except Exception as e:
        if not os.path.exists(f"{result_id}/error.txt"):
            os.mkdir(result_id)
            with open(f"{result_id}/error.txt", "w", encoding="utf-8") as f:
                f.write(str(e))
        else:
            with open(f"{result_id}/error.txt", "a", encoding="utf-8") as f:
                f.write(str(e))
        with open(f"{result_id}/error.txt", "rb") as f:
            error_file = f.read()
        req_files = {
            "error.txt": error_file,
        }
        requests.post(api_url+f"?error={True}", data={"result_id": result_id, "error": str(e)}, files=req_files, timeout=120, verify=False, headers={"Authorization":user_token})
