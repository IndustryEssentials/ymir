import json
import os
import shutil
from typing import Dict

import yaml
from PIL import Image
from google.protobuf import json_format

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import code, utils, checker
from controller.utils.app_logger import logger
from proto import backend_pb2


class InferenceCMDInvoker(BaseMirControllerInvoker):
    @classmethod
    def gen_inference_config(cls, req_inference_config: str, work_dir: str) -> str:
        inference_config = yaml.safe_load(req_inference_config)
        inference_config_file = os.path.join(work_dir, "inference_config.yaml")
        with open(inference_config_file, "w") as f:
            yaml.dump(inference_config, f)

        return inference_config_file

    @classmethod
    def check_picture(cls, one_picture: str) -> bool:
        img = Image.open(one_picture)
        img_type = img.format.lower()
        if img_type in ["png", "jpeg", "jpg"]:
            return True
        else:
            logger.warning(f"image error: {one_picture}")
            return False

    @classmethod
    def prepare_inference_picture(cls, source_path: str, work_dir: str) -> str:
        inference_picture_directory = os.path.join(work_dir, "inference_picture")
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

    @classmethod
    def get_inference_result(cls, work_dir: str) -> Dict:
        infer_result_file = os.path.join(work_dir, "out", "infer-result.json")
        with open(infer_result_file) as f:
            infer_result = json.load(f)

        return infer_result

    @classmethod
    def generate_inference_response(cls, inference_result: Dict) -> backend_pb2.GeneralResp:
        resp = utils.make_general_response(code.ResCode.CTR_OK, "")
        result = dict(imageAnnotations=inference_result["detection"])
        resp_inference = backend_pb2.RespCMDInference()
        json_format.ParseDict(result, resp_inference, ignore_unknown_fields=False)
        resp.detection.CopyFrom(resp_inference)

        return resp

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID, checker.Prerequisites.CHECK_REPO_ID],
            mir_root=self._repo_root,
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        index_file = self.prepare_inference_picture(self._request.asset_dir, self._work_dir)
        config_file = self.gen_inference_config(self._request.model_config, self._work_dir)

        self.inference_cmd(
            work_dir=self._work_dir,
            config_file=config_file,
            model_location=self._assets_config["modelskvlocation"],
            model_hash=self._request.model_hash,
            index_file=index_file,
            executor=self._assets_config["mining_image"],
        )
        inference_result = self.get_inference_result(self._work_dir)

        return self.generate_inference_response(inference_result)

    @classmethod
    def inference_cmd(cls, work_dir: str, model_location: str, config_file: str, model_hash: str, index_file: str,
                      executor: str) -> backend_pb2.GeneralResp:
        infer_cmd = (f"{utils.mir_executable()} infer -w {work_dir} --model-location {model_location} --index-file "
                     f"{index_file} --model-hash {model_hash} --config-file {config_file} --executor {executor}")
        return utils.run_command(infer_cmd)

    def _repr(self) -> str:
        return (f"cmd_inference: user: {self._request.user_id}, task_id: {self._task_id} "
                f"model_hash: {self._request.model_hash}")
