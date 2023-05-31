import os
import shutil

import yaml
from PIL import Image

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import utils, checker
from id_definition.error_codes import CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2


class InferenceCMDInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return True

    @classmethod
    def gen_inference_config(cls, req_inference_config: str, task_context: dict,
                             object_type: "mir_cmd_pb.ObjectType.V", work_dir: str) -> str:
        executor_config = yaml.safe_load(req_inference_config)
        executor_config["object_type"] = object_type
        task_context["object_type"] = object_type

        inference_config_file = os.path.join(work_dir, "inference_config.yaml")
        with open(inference_config_file, "w") as f:
            yaml.dump({'executor_config': executor_config, 'task_context': task_context}, f, allow_unicode=True)

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
                                                object_type=self._request.object_type,
                                                work_dir=self._work_dir)

        self.inference_cmd(
            repo_root=self._repo_root,
            label_storage_file=self._label_storage_file,
            work_dir=self._work_dir,
            config_file=config_file,
            model_location=self._assets_config["modelskvlocation"],
            model_hash=self._request.model_hash,
            model_stage=self._request.model_stage,
            index_file=index_file,
            executor=self._request.singleton_op,
        )

        infer_result_pb_path = os.path.join(self._work_dir, "out", "prediction.mir")
        if not os.path.isfile(infer_result_pb_path):
            return utils.make_general_response(CTLResponseCode.RUN_COMMAND_ERROR,
                                               f"Inference result not found: {infer_result_pb_path}")
        infer_result = mir_cmd_pb.InferResultAnnotations()
        with open(infer_result_pb_path, 'rb') as f:
            infer_result.ParseFromString(f.read())
        prediction = infer_result.prediction
        unknown_prediction = infer_result.unknown_types_prediction

        # add prediction with unknown types
        for asset_id, sia in unknown_prediction.image_annotations.items():
            for anno in sia.boxes:
                anno.index = len(prediction.image_annotations[asset_id].boxes)
                prediction.image_annotations[asset_id].boxes.append(anno)

        resp = utils.make_general_response(CTLResponseCode.CTR_OK, "")
        for asset_id, sia in prediction.image_annotations.items():
            resp.objects.image_annotations[asset_id].CopyFrom(sia)

        os.remove(infer_result_pb_path)

        return resp

    @classmethod
    def inference_cmd(cls, repo_root: str, label_storage_file: str, work_dir: str, model_location: str,
                      config_file: str, model_hash: str, model_stage: str, index_file: str,
                      executor: str) -> backend_pb2.GeneralResp:
        infer_cmd = [
            utils.mir_executable(), 'infer', '--root', repo_root, '--user-label-file', label_storage_file, '-w',
            work_dir, '--model-location', model_location, '--index-file', index_file, '--model-hash',
            f"{model_hash}@{model_stage}", '--task-config-file', config_file, "--executor", executor
        ]
        return utils.run_command(infer_cmd)
