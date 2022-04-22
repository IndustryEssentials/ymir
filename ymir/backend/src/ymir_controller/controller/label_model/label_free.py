import glob
import json
import logging
import os
import shutil
import zipfile
from io import BytesIO
from typing import Dict, List
from xml.etree import ElementTree

from controller.label_model.base import LabelBase, catch_label_task_error
from controller.label_model.request_handler import RequestHandler


class LabelFree(LabelBase):
    def __init__(self, request_handler: RequestHandler = RequestHandler()) -> None:
        self._requests = request_handler

    @staticmethod
    def gen_detection_label_config(keywords: List) -> str:
        """
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
        # Create a project and set up the labeling interface
        url_path = "/api/projects"
        label_config = self.gen_detection_label_config(keywords)
        data = dict(
            title=project_name,
            collaborators=collaborators,
            label_config=label_config,
            expert_instruction=f"<a target='_blank' href='{expert_instruction}'>Labeling Guide</a>",
        )
        resp = self._requests.post(url_path=url_path, json_data=data)
        project_id = json.loads(resp).get("id")
        if not isinstance(project_id, int):
            raise ValueError(f"LabelFree return wrong id: {project_id} from {url_path}")

        return project_id

    def set_import_storage(self, project_id: int, import_path: str, use_pre_annotation: bool = False) -> int:
        # Create a new local file import storage connection
        url_path = "/api/storages/localfiles"
        data = dict(
            path=import_path,
            use_blob_urls=True,
            title="input_dir",
            project=project_id,
            regex_filter=".*(jpe?g|png|bmp)",
            description="description",
            use_pre_annotation=use_pre_annotation,
        )

        resp = self._requests.post(url_path=url_path, json_data=data)
        storage_id = json.loads(resp).get("id")
        if not isinstance(storage_id, int):
            raise ValueError(f"LabelFree return wrong id: {storage_id} from {url_path}")
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

        resp = self._requests.post(url_path=url_path, json_data=data)
        exported_storage_id = json.loads(resp).get("id")
        if not isinstance(exported_storage_id, int):
            raise ValueError(f"LabelFree return wrong id: {exported_storage_id} from {url_path}")

        return exported_storage_id

    def sync_import_storage(self, storage_id: int) -> None:
        # Sync tasks from a local file import storage connection
        url_path = f"/api/storages/localfiles/{storage_id}/sync"
        self._requests.post(url_path=url_path)

    def sync_export_storage(self, storage_id: int) -> None:
        # Sync tasks from a local file export storage connection
        url_path = f"/api/storages/export/localfiles/{storage_id}/sync"
        self._requests.post(url_path=url_path)

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
        resp = self._requests.get(url_path=url_path)
        return json.loads(resp)

    def delete_unlabeled_task(self, project_id: int) -> None:
        url_path = f"/api/projects/{project_id}"
        self._requests.put(url_path=url_path, params={"delete_unlabeled_task": True})

    @classmethod
    def _move_voc_files(cls, des_path: str) -> None:
        voc_files = glob.glob(f"{des_path}/**/*.xml")
        for voc_file in voc_files:
            base_name = os.path.basename(voc_file)
            shutil.move(voc_file, os.path.join(des_path, base_name))

    @classmethod
    def unzip_annotation_files(cls, content: BytesIO, des_path: str) -> None:
        with zipfile.ZipFile(content, mode="r") as zf:
            for names in zf.namelist():
                zf.extract(names, des_path)

        cls._move_voc_files(des_path)

    def convert_annotation_to_voc(self, project_id: int, des_path: str) -> None:
        url_path = f"/api/projects/{project_id}/export?exportType=VOC"
        resp = self._requests.get(url_path=url_path)
        self.unzip_annotation_files(BytesIO(resp), des_path)

        logging.info(f"success convert_annotation_to_ymir: {des_path}")

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
        logging.info("start LABELFREE run()")
        project_id = self.create_label_project(project_name, keywords, collaborators, expert_instruction)
        storage_id = self.set_import_storage(project_id, input_asset_dir, use_pre_annotation)
        exported_storage_id = self.set_export_storage(project_id, export_path)
        self.sync_import_storage(storage_id)
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
