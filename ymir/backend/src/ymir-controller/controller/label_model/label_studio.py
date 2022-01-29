import glob
import json
import logging
import math
import os
import shutil
import zipfile
from io import BytesIO
from typing import Dict, List
from xml.etree import ElementTree

from controller.config import label_task as label_task_config
from controller.label_model.base import LabelBase, catch_label_task_error
from controller.label_model.request_handler import RequestHandler


class LabelStudio(LabelBase):
    # https://labelstud.io/api/
    def __init__(self, request_handler: RequestHandler = RequestHandler()) -> None:
        self.requests = request_handler

    @staticmethod
    def gen_detection_label_config(keywords: List) -> str:
        """
        gen detection label config according to label studio https://labelstud.io/playground/
        <View>
          <Image name="image" value="$image"/>
          <RectangleLabels name="label" toName="image">
            <Label value="Airplane" background="green"/>
            <Label value="Car" background="blue"/>
          </RectangleLabels>
        </View>
        """
        top = ElementTree.Element("View")
        image_leyer = ElementTree.Element("Image", name="image", value="$image", crosshair="true", maxwidth="100%")
        rectangle_labels_layer = ElementTree.Element("RectangleLabels", name="label", toName="image")
        children_label_content = [
            ElementTree.Element("Label", value=keyword, background="green") for keyword in keywords
        ]
        rectangle_labels_layer.extend(children_label_content)
        top.extend([image_leyer, rectangle_labels_layer])

        label_config = ElementTree.tostring(top, encoding="unicode")

        return label_config

    def create_label_project(
        self, project_name: str, keywords: List, collaborators: List, expert_instruction: str, **kwargs: Dict
    ) -> int:
        # Create a project and set up the labeling interface in Label Studio
        url_path = "/api/projects"
        label_config = self.gen_detection_label_config(keywords)
        data = dict(
            title=project_name,
            collaborators=collaborators,
            label_config=label_config,
            expert_instruction=f"<a target='_blank' href='{expert_instruction}'>Labeling Guide</a>",
        )
        resp = self.requests.post(url_path=url_path, json_data=data)
        project_id = json.loads(resp)["id"]

        return project_id

    def set_import_storage(self, project_id: int, import_path: str) -> int:
        # Create a new local file import storage connection
        url_path = "/api/storages/localfiles"
        data = dict(
            path=import_path,
            use_blob_urls=True,
            title="input_dir",
            project=project_id,
            regex_filter=".*(jpe?g|png|bmp)",
            description="description",
        )

        resp = self.requests.post(url_path=url_path, json_data=data)
        storage_id = json.loads(resp)["id"]

        return storage_id

    def set_export_storage(self, project_id: int, export_path: str) -> int:
        # Create a new local file export storage connection to store annotations
        url_path = "/api/storages/export/localfiles"
        data = dict(
            path=export_path,
            use_blob_urls=True,
            title="output_dir",
            project=project_id,
            regex_filter=".*(jpe?g|png|bmp)",
            description="description",
        )

        resp = self.requests.post(url_path=url_path, json_data=data)
        exported_storage_id = json.loads(resp)["id"]

        return exported_storage_id

    def update_prediction(self, task_id: int, predictions: List) -> Dict:
        # Create a prediction for a specific task.
        url_path = "/api/predictions"
        data = dict(
            model_version="", result=predictions, score=0, cluster=0, neighbors={}, mislabeling=0, task=task_id,
        )

        resp = self.requests.post(url_path=url_path, json_data=data)

        return json.loads(resp)

    def sync_import_storage(self, storage_id: int) -> None:
        # Sync tasks from a local file import storage connection
        url_path = f"/api/storages/localfiles/{storage_id}/sync"
        self.requests.post(url_path=url_path)

    def sync_export_storage(self, storage_id: int) -> None:
        # Sync tasks from a local file export storage connection
        url_path = f"/api/storages/export/localfiles/{storage_id}/sync"
        self.requests.post(url_path=url_path)

    def get_task_completion_percent(self, project_id: int) -> float:
        def safe_div(a: int, b: int) -> float:
            if b == 0:
                return 1.0
            return a / b

        content = self.get_project_info(project_id)
        percent = safe_div(content["num_tasks_with_annotations"], content["task_number"])

        return percent

    def get_project_info(self, project_id: int) -> Dict:
        url_path = f"/api/projects/{project_id}"
        resp = self.requests.get(url_path=url_path)
        return json.loads(resp)

    def get_project_tasks(self, project_id: int, unlabelled_only: bool = False) -> List:
        project_info = self.get_project_info(project_id)
        task_num = project_info["task_number"]
        url_path = f"/api/projects/{project_id}/tasks/"

        tasks = []
        for page in range(1, math.ceil(task_num / label_task_config.LABEL_PAGE_SIZE) + 1):
            params = {
                "page_size": label_task_config.LABEL_PAGE_SIZE,
                "page": page,
            }
            all_content = self.requests.get(url_path=url_path, params=params)
            for content in json.loads(all_content):
                if unlabelled_only and content["is_labeled"]:
                    continue
                tasks.append(content)

        logging.info(f"retrieved {len(tasks)} tasks in project {project_id} unlabelled_only: {unlabelled_only}")

        return tasks

    def delete_unlabeled_task(self, project_id: int) -> None:
        unlabeled_tasks = self.get_project_tasks(project_id=project_id, unlabelled_only=True)

        # label studio strange behavior, post [] will delete all tasks.
        if not unlabeled_tasks:
            return None
        unlabeled_task_ids = [task["id"] for task in unlabeled_tasks]
        url_path = "/api/dm/actions"
        params = {"id": "delete_tasks", "project": project_id}
        json_data = {
            "ordering": [],
            "selectedItems": {"all": False, "included": unlabeled_task_ids},
            "filters": {"conjunction": "and", "items": []},
            "project": str(project_id),
        }

        self.requests.post(url_path=url_path, params=params, json_data=json_data)

    @classmethod
    def _move_label_studio_voc_files(cls, des_path: str) -> None:
        voc_files = glob.glob(f"{des_path}/**/*.xml")
        for voc_file in voc_files:
            base_name = os.path.basename(voc_file)
            shutil.move(voc_file, os.path.join(des_path, base_name))

    @classmethod
    def unzip_annotation_files(cls, content: BytesIO, des_path: str) -> None:
        with zipfile.ZipFile(content, mode="r") as zf:
            for names in zf.namelist():
                zf.extract(names, des_path)

        cls._move_label_studio_voc_files(des_path)

    def convert_annotation_to_voc(self, project_id: int, des_path: str) -> None:
        url_path = f"/api/projects/{project_id}/export?exportType=VOC"
        resp = self.requests.get(url_path=url_path)
        self.unzip_annotation_files(BytesIO(resp), des_path)

        logging.info(f"success convert_annotation_to_ymir: {des_path}")

    def update_project_prediction(self, input_asset_dir: str, project_id: int) -> None:
        map_filename_prediction = {}
        for json_file_relative in os.listdir(input_asset_dir):
            if not json_file_relative.endswith(".json"):
                continue
            json_file_abs = os.path.join(input_asset_dir, json_file_relative)
            if not os.path.isfile(json_file_abs):
                continue
            with open(json_file_abs) as f:
                json_content = json.load(f)
            predictions = json_content["predictions"][0]["result"]
            if not predictions:
                continue
            map_filename_prediction[os.path.basename(json_content["data"]["image"])] = predictions

        tasks = self.get_project_tasks(project_id)
        valid_prediction_cnt = 0
        for task in tasks:
            asset_name = os.path.basename(task["data"]["image"])
            predictions = map_filename_prediction.get(asset_name, [])
            if not predictions:
                continue
            task_id = task["id"]
            self.update_prediction(task_id, predictions)
            valid_prediction_cnt += 1

        logging.info(f"successful created {valid_prediction_cnt} predictions.")

    @catch_label_task_error
    def run(
        self,
        task_id: str,
        project_name: str,
        keywords: List,
        collaborators: List,
        expert_instruction: str,
        input_asset_dir: str,
        export_path: str,
        monitor_file_path: str,
        repo_root: str,
        media_location: str,
        import_work_dir: str,
        use_pre_annotation: bool,
    ) -> None:
        logging.info("start LabelStudio run()")
        project_id = self.create_label_project(project_name, keywords, collaborators, expert_instruction)
        storage_id = self.set_import_storage(project_id, input_asset_dir)
        exported_storage_id = self.set_export_storage(project_id, export_path)
        self.sync_import_storage(storage_id)
        if use_pre_annotation:
            self.update_project_prediction(input_asset_dir, project_id)
        self.store_label_task_mapping(
            project_id,
            task_id,
            monitor_file_path,
            export_path,
            repo_root,
            media_location,
            import_work_dir,
            exported_storage_id,
        )
