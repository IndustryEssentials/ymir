from typing import Dict, List, Union

from app.utils.cache import CacheClient
from app.utils.ymir_controller import ControllerClient
from common_utils.labels import SingleLabel, UserLabels


def upsert_labels(
    user_id: int,
    new_labels: UserLabels,
    controller_client: ControllerClient,
    dry_run: bool = False,
) -> Dict:
    """
    update or insert labels
    """
    resp = controller_client.add_labels(user_id, new_labels, dry_run)

    conflict_labels = []
    if resp.get("label_collection"):
        for conflict_label in resp["label_collection"]["labels"]:
            conflict_labels += [conflict_label["name"]] + conflict_label["aliases"]

    return {"failed": conflict_labels}


def ensure_labels_exist(
    user_id: int,
    user_labels: UserLabels,
    controller_client: ControllerClient,
    keywords: List[str],
    cache: CacheClient,
) -> List[int]:
    try:
        return keywords_to_class_ids(user_labels, keywords)
    except ValueError:
        new_labels = UserLabels(labels=[SingleLabel(name=k) for k in keywords])
        upsert_labels(user_id=user_id, new_labels=new_labels, controller_client=controller_client)
        user_labels = controller_client.get_labels_of_user(user_id)
        cache.delete_personal_keywords_cache()
    return keywords_to_class_ids(user_labels, keywords)


def keywords_to_class_ids(user_labels: UserLabels, keywords: List[str]) -> List[int]:
    class_ids, _ = user_labels.id_for_names(names=keywords, raise_if_unknown=True)
    return class_ids


def class_ids_to_keywords(user_labels: UserLabels, class_ids: List) -> List[str]:
    return user_labels.main_name_for_ids(class_ids=[int(i) for i in class_ids])


def class_id_to_keyword(user_labels: UserLabels, class_id: Union[int, str]) -> List[str]:
    return user_labels.main_name_for_id(class_id=int(class_id))
