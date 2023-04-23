import random
import string
from typing import Dict, Optional


def random_lower_string(k: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=k))


def random_hash(hash_type: str = "asset") -> str:
    leading = hash_type[0]
    return leading + "0" * 9 + random_lower_string(40)


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_url() -> str:
    return f"https://www.{random_lower_string()}.com/{random_lower_string()}"


def get_normal_token_headers() -> Dict[str, str]:
    headers = {"X-User-Id": "233", "X-User-Role": "1"}
    return headers


def get_admin_token_headers() -> Dict[str, str]:
    headers = {"X-User-Id": "233", "X-User-Role": "2"}
    return headers


def get_super_admin_token_headers() -> Dict[str, str]:
    headers = {"X-User-Id": "233", "X-User-Role": "3"}
    return headers


def gen_task_data(task_id: Optional[int] = 1, result: Optional[Dict] = None) -> Dict:
    result = result or {"result_dataset": {"id": 20, "dataset_group_id": 1}}
    task_info = {
        "id": task_id,
        "type": 1,
        "state": 3,
        "duration": 20,
        "percent": 1,
        "user_id": 233,
        "is_terminated": False,
    }
    task_info.update(result)
    return task_info


def gen_dataset_data(dataset_id: Optional[int] = 1) -> Dict:
    dataset = {
        "id": dataset_id,
        "name": random_lower_string(),
        "project_id": 1,
        "user_id": 233,
    }
    return dataset


def gen_dataset_version_data(version_id: Optional[int] = 1) -> Dict:
    data = {
        "id": version_id,
        "task_id": 1,
        "result_state": 1,
        "object_type": 3,
        "keyword_count": 2,
    }
    return data


def gen_model_version_data(version_id: Optional[int] = 1) -> Dict:
    data = {
        "id": version_id,
        "task_id": 1,
        "result_state": 1,
        "object_type": 3,
        "url": random_url(),
        "keywords": ["person", "cat"],
    }
    return data


def gen_model_data(model_id: Optional[int] = 1) -> Dict:
    model = {
        "id": model_id,
    }
    return model


def gen_prediction_data(prediction_id: Optional[int] = 1) -> Dict:
    prediction = {
        "id": prediction_id,
        "object_type": 3,
        "dataset_id": 1,
        "model_id": 1,
        "task_id": 1,
        "source": 1,
        "asset_count": 1,
        "class_name_count": 1,
        "class_names": ["cat"],
    }
    return prediction


def gen_project_data(project_id: Optional[int] = 1) -> Dict:
    project = {
        "id": project_id,
        "object_type": 3,
    }
    return project


def gen_docker_image_data(docker_image_id: Optional[int] = 1) -> Dict:
    docker_image = {
        "id": docker_image_id,
        "object_type": 3,
        "url": random_url(),
        "state": 1,
        "result_state": 1,
        "configs": [{"config": {}, "object_type": 3, "type": 1}],
    }
    return docker_image
