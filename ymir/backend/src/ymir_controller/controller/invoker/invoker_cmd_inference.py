import json
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
    def prepare_inference_assets(cls, asset_dir: str, dst_dir: str) -> str:
        dst_assets = os.path.join(dst_dir, "assets")
        os.makedirs(dst_assets, exist_ok=True)

        media_files = []
        for root, _, files in os.walk(asset_dir):
            for asset_fileame in files:
                asset_src_file = os.path.join(root, asset_fileame)

                if Image.open(asset_src_file).format.lower() in ["png", "jpeg", "jpg"]:
                    shutil.copy(asset_src_file, dst_assets)
                    media_files.append(os.path.join(dst_assets, asset_fileame))

        index_file = os.path.join(dst_dir, "index.txt")
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

        index_file = self.prepare_inference_assets(asset_dir=self._request.asset_dir, dst_dir=self._work_dir)
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
            return utils.make_general_response(CTLResponseCode.DOCKER_IMAGE_ERROR, "inference result not found.")
        with open(infer_result_file) as f:
            infer_result = json.load(f)

        resp = utils.make_general_response(CTLResponseCode.CTR_OK, "")
        detections = infer_result.get("detection")
        if not isinstance(detections, dict):
            return resp

        # class_id should be updated, as it was from outside model.
        for _, annos_dict in detections.items():
            if "annotations" in annos_dict:
                if "boxes" not in annos_dict:
                    annos_dict["boxes"] = annos_dict["annotations"]
                del annos_dict["annotations"]

            annos = annos_dict.get("boxes", [])
            for annotation in annos:
                annotation["class_id"] = self._user_labels.id_for_names(names=annotation["class_name"],
                                                                        raise_if_unknown=False)[0][0]

        json_format.ParseDict(dict(image_annotations=detections), resp.detection, ignore_unknown_fields=False)

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
