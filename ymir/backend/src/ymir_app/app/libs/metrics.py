from typing import List

from fastapi.logger import logger

from app.utils.ymir_viz import VizClient


def send_keywords_metrics(
    user_id: int,
    project_id: int,
    task_hash: str,
    keyword_ids: List[int],
    create_time: int,
) -> None:
    try:
        viz_client = VizClient(user_id=user_id, project_id=project_id)
        viz_client.send_metrics(
            metrics_group="task",
            id=task_hash,
            create_time=create_time,
            keyword_ids=keyword_ids,
        )
    except Exception:
        logger.exception(
            "[metrics] failed to send keywords(%s) stats to viewer, continue anyway",
            keyword_ids,
        )


def send_project_metrics(
    user_id: int,
    project_id: int,
    project_name: str,
    keyword_ids: List[int],
    project_type: str,
    create_time: int,
) -> None:
    try:
        viz_client = VizClient()
        viz_client.initialize(user_id=user_id, project_id=project_id)
        viz_client.send_metrics(
            metrics_group="project",
            id=f"{project_id:0>6}",
            create_time=create_time,
            keyword_ids=keyword_ids,
            extra_data={"project_type": project_type},
        )
    except Exception:
        logger.exception(
            "[metrics] failed to send project(%s) stats to viewer, continue anyway",
            project_name,
        )
