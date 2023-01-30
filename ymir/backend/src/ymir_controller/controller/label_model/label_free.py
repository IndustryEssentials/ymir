import glob
import json
import logging
import os
import shutil
import zipfile
from enum import IntEnum
from io import BytesIO
from pathlib import Path
from typing import Dict, List
from xml.etree import ElementTree

from mir.protos import mir_command_pb2 as mir_cmd_pb
from controller.label_model.base import LabelBase, catch_label_task_error, NotReadyError
from controller.label_model.request_handler import RequestHandler


class LabelFreeProjectType(IntEnum):
    detection = 1
    semantic_segmentation = 2
    instance_segmentation = 4


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

    @staticmethod
    def map_object_type_to_label_free_project_type(object_type: int, is_instance_segmentation: bool) -> int:
        if is_instance_segmentation:
            project_type = LabelFreeProjectType.instance_segmentation
        elif object_type == mir_cmd_pb.ObjectType.OT_DET_BOX:
            project_type = LabelFreeProjectType.detection
        elif object_type == mir_cmd_pb.ObjectType.OT_SEG:
            project_type = LabelFreeProjectType.semantic_segmentation
        else:
            raise ValueError(f"LabelFree DOES NOT SUPPORT object_type({object_type})")
        return project_type.value

    def create_label_project(
        self,
        project_name: str,
        keywords: List,
        collaborators: List,
        expert_instruction: str,
        object_type: int,
        is_instance_segmentation: bool,
    ) -> int:
        # Create a project and set up the labeling interface
        url_path = "/api/projects"
        label_config = self.gen_detection_label_config(keywords)
        data = dict(
            title=project_name,
            collaborators=collaborators,
            label_config=label_config,
            expert_instruction=f"<a target='_blank' href='{expert_instruction}'>Labeling Guide</a>",
            project_type=self.map_object_type_to_label_free_project_type(object_type, is_instance_segmentation),
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
        logging.info("label task percent info: %s", content)
        percent = safe_div(content["num_tasks_with_annotations"], content["task_number"])

        return percent

    def get_project_info(self, project_id: int) -> Dict:
        url_path = f"/api/projects/{project_id}"
        resp = self._requests.get(url_path=url_path)
        return json.loads(resp)

    def delete_unlabeled_task(self, project_id: int) -> None:
        url_path = f"/api/projects/{project_id}"
        self._requests.put(url_path=url_path, params={"delete_unlabeled_task": True})

    @staticmethod
    def _move_voc_annotations_to(des_path: str) -> None:
        voc_files = glob.glob(f"{des_path}/**/*.xml")
        for voc_file in voc_files:
            base_name = os.path.basename(voc_file)
            shutil.move(voc_file, os.path.join(des_path, base_name))

    @staticmethod
    def _move_coco_annotations_to(des_path: str) -> None:
        """
        Convert result.json (Label Studio default filename) to coco-annotations.json (YMIR required filename)
        """
        coco_json_file = Path(des_path) / "annotations/stuff_images.json"
        coco_json_file.rename(Path(des_path) / "coco-annotations.json")

    @classmethod
    def unzip_annotation_files(cls, content: BytesIO, des_path: str) -> None:
        with zipfile.ZipFile(content, mode="r") as zf:
            for names in zf.namelist():
                zf.extract(names, des_path)

    def fetch_label_result(self, project_id: int, object_type: int, des_path: str) -> None:
        export_task_id = self.get_export_task(project_id, object_type)
        export_url = self.get_export_url(project_id, export_task_id)
        content = self._requests.get(export_url)
        self.unzip_annotation_files(BytesIO(content), des_path)
        if object_type == mir_cmd_pb.ObjectType.OT_DET_BOX:
            self._move_voc_annotations_to(des_path)
        else:
            self._move_coco_annotations_to(des_path)
        logging.info(f"success save label result from labelfree to {des_path}")

    def get_export_task(self, project_id: int, object_type: int) -> str:
        url_path = "/api/v1/export"
        params = {"project_id": project_id, "page_size": 1}
        content = self._requests.get(url_path=url_path, params=params)
        export_tasks = json.loads(content)["data"]["export_tasks"]
        if export_tasks:
            return export_tasks[0]["task_id"]
        else:
            self.create_export_task(project_id, object_type)
            raise NotReadyError()

    def create_export_task(self, project_id: int, object_type: int) -> None:
        url_path = "/api/v1/export"
        export_type = 1 if object_type == mir_cmd_pb.ObjectType.OT_DET_BOX else 4
        payload = {"project_id": project_id, "export_type": export_type, "export_image": False}
        resp = self._requests.post(url_path=url_path, json_data=payload)
        try:
            export_task_id = json.loads(resp)["data"]["task_id"]
        except Exception:
            logging.exception("failed to create export task for label project %s", project_id)
        else:
            logging.info("created export task %s for label project %s", export_task_id, project_id)

    def get_export_url(self, project_id: int, export_task_id: str) -> str:
        url_path = f"/api/v1/export/{export_task_id}"
        content = self._requests.get(url_path=url_path)
        try:
            export_url = json.loads(content)["data"]["store_path"]
        except Exception:
            logging.info("label task %s not finished", export_task_id)
            raise NotReadyError()
        # FIXME ad hoc walkaround
        return export_url.replace("None", "")

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
        object_type: int,
        is_instance_segmentation: bool,
    ) -> None:
        logging.info("start LABELFREE run()")
        project_id = self.create_label_project(
            project_name, keywords, collaborators, expert_instruction, object_type, is_instance_segmentation)
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
            input_asset_dir,
            object_type,
        )
