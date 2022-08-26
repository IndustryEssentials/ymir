import json
import logging
import os
import shutil

import yaml
from PIL import Image
from google.protobuf import json_format

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils, checker
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class InferenceCMDInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return True

    @classmethod
    def gen_inference_config(cls, req_inference_config: str, task_context: dict, work_dir: str) -> str:
        inference_config = yaml.safe_load(req_inference_config)
        inference_config_file = os.path.join(work_dir, "inference_config.yaml")
        with open(inference_config_file, "w") as f:
            yaml.dump({'executor_config': inference_config, 'task_context': task_context}, f)

        return inference_config_file

    @classmethod
    def check_picture(cls, one_picture: str) -> bool:
        img = Image.open(one_picture)
        img_type = img.format.lower()
        if img_type in ["png", "jpeg", "jpg"]:
            return True
        else:
            logging.warning(f"image error: {one_picture}")
            return False

    @classmethod
    def prepare_inference_picture(cls, source_path: str, work_dir: str) -> str:
        inference_picture_directory = os.path.join(work_dir, "assets")
        os.makedirs(inference_picture_directory, exist_ok=True)

        for root, _, files in os.walk(source_path):
            for one_pic in files:
                media_file = os.path.join(root, one_pic)
                if cls.check_picture(media_file):
                    shutil.copy(media_file, inference_picture_directory)

        media_files = [os.path.join(inference_picture_directory, f) for f in os.listdir(inference_picture_directory)]
        index_file = os.path.join(work_dir, "inference_pic_index.txt")
        with open(index_file, "w") as f:
            f.write("\n".join(media_files))

        return index_file

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(
            invoker=self,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID, checker.Prerequisites.CHECK_REPO_ID],
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        if not self._user_labels:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, "invalid _user_labels")

        index_file = self.prepare_inference_picture(self._request.asset_dir, self._work_dir)
        config_file = self.gen_inference_config(req_inference_config=self._request.docker_image_config,
                                                task_context={'server_runtime': self._assets_config['server_runtime']},
                                                work_dir=self._work_dir)

        self.inference_cmd(
            repo_root=self._repo_root,
            work_dir=self._work_dir,
            config_file=config_file,
            model_location=self._assets_config["modelskvlocation"],
            model_hash=self._request.model_hash,
            model_stage=self._request.model_stage,
            index_file=index_file,
            executor=self._request.singleton_op,
        )

        infer_result_file = os.path.join(self._work_dir, "out", "infer-result.json")
        if not os.path.isfile(infer_result_file):
            return utils.make_general_response(CTLResponseCode.DOCKER_IMAGE_ERROR, "empty inference result.")
        with open(infer_result_file) as f:
            infer_result = json.load(f)

        resp = utils.make_general_response(CTLResponseCode.CTR_OK, "")
        json_format.ParseDict(dict(imageAnnotations=infer_result["detection"]),
                              resp.detection,
                              ignore_unknown_fields=False)

        # class_id should be updated, as it was from outside model.
        for _, annotations in resp.detection.image_annotations.items():
            for annotation in annotations.annotations:
                annotation.class_id = self._user_labels.get_class_ids(annotation.class_name, raise_if_unknown=False)[0]

        return resp

    @classmethod
    def inference_cmd(cls, repo_root: str, work_dir: str, model_location: str, config_file: str, model_hash: str,
                      model_stage: str, index_file: str, executor: str) -> backend_pb2.GeneralResp:
        infer_cmd = [
            utils.mir_executable(), 'infer', '--root', repo_root, '-w', work_dir, '--model-location', model_location,
            '--index-file', index_file, '--model-hash', f"{model_hash}@{model_stage}", '--task-config-file',
            config_file, "--executor", executor
        ]
        return utils.run_command(infer_cmd)
