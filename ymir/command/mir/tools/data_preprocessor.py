import hashlib
import io
import shutil
import sys
from typing import Dict

from PIL import Image

from mir.protos import mir_command_pb2 as mirpb


# private: prep functions
def _prep_img_longside_resize(img: Image, dest_size: int) -> Image:
    orig_width, orig_height = img.size

    dest_width, dest_height = dest_size, dest_size
    if orig_width >= orig_height:
        dest_height = int(orig_height * dest_width / orig_width)
    else:
        dest_width = int(orig_width * dest_height / orig_height)

    return img.resize(size=(dest_width, dest_height))


def _prep_pbs_longside_resize(attrs: mirpb.MetadataAttributes, image_annotations: mirpb.SingleImageAnnotations,
                              gt_annotations: mirpb.SingleImageAnnotations, dest_size: int) -> None:
    ratio: float
    if attrs.width >= attrs.height:
        ratio = dest_size / attrs.width
        attrs.height = int(attrs.height * ratio)
        attrs.width = dest_size
    else:
        ratio = dest_size / attrs.height
        attrs.width = int(attrs.width * ratio)
        attrs.height = dest_size

    for annotation in image_annotations.annotations:
        _resize_annotation(annotation, ratio)

    for annotation in gt_annotations.annotations:
        _resize_annotation(annotation, ratio)


def _resize_annotation(annotation: mirpb.Annotation, ratio: float) -> None:
    annotation.box.x = int(annotation.box.x * ratio)
    annotation.box.y = int(annotation.box.y * ratio)
    annotation.box.w = int(annotation.box.w * ratio)
    annotation.box.h = int(annotation.box.h * ratio)


class DataPreprocessor:
    def __init__(self, args: Dict[str, dict] = {}) -> None:
        """
        init a dpp
        args: {'longside_resize': {'dest_size': xxx}}
        """
        self._op_args = [(k, v) for k, v in args.items()]
        self._op_args_signature = hashlib.md5(str(self._op_args).encode('utf-8')).hexdigest()[-6:]

    @property
    def signature(self) -> str:
        return self._op_args_signature if self.need_prep else ''

    @property
    def need_prep(self) -> bool:
        return len(self._op_args) > 0

    def prep_img(self, src_img_path: str, dest_img_path: str = '', return_bytes: bool = True) -> bytes:
        """
        preprocess, copy preprocessed image to dest_img_path, or return bytes of preprocessed image
        """
        if not self.need_prep:
            if dest_img_path:
                shutil.copyfile(src_img_path, dest_img_path)

            # if wants to return bytes
            if return_bytes:
                with open(src_img_path, 'rb') as f:
                    return f.read()
            return b''

        # if need prep
        img = Image.open(src_img_path)
        orig_img_format = img.format

        for op_name, op_args in self._op_args:
            func = getattr(sys.modules[__name__], f"_prep_img_{op_name}")
            img = func(img=img, **op_args)

        if dest_img_path:
            with open(dest_img_path, 'wb') as f:
                img.save(dest_img_path, format=orig_img_format)
        # if wants to return bytes
        if return_bytes:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=orig_img_format)
            return img_bytes.getvalue()
        return b''

    def prep_pbs(self, attrs: mirpb.MetadataAttributes, image_annotations: mirpb.SingleImageAnnotations,
                 gt_annotations: mirpb.SingleImageAnnotations) -> None:
        if not self.need_prep:
            return
        for op_name, op_args in self._op_args:
            func = getattr(sys.modules[__name__], f"_prep_pbs_{op_name}")
            func(attrs=attrs, image_annotations=image_annotations, gt_annotations=gt_annotations, **op_args)
