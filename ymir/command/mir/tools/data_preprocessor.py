import io
import shutil

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
    def __init__(self, args: dict = {}) -> None:
        """
        init a dpp
        args: {'longside_resize': {'dest_size': xxx}}
        """
        self._lr_dest_size = args.get('longside_resize', {}).get('dest_size', 0)

    @property
    def id(self) -> str:
        return f"lr{self._lr_dest_size}" if self._lr_dest_size > 0 else ''

    @property
    def need_prep(self) -> bool:
        return self._lr_dest_size > 0

    @classmethod
    def _read(cls, img_path: str) -> Image:
        return Image.open(img_path)

    @classmethod
    def _save(cls, img: Image, format: str) -> bytes:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        return img_bytes.getvalue()

    def prep_img(self, src_img_path: str, dest_img_path: str) -> bytes:
        """
        preprocess, copy preprocessed image to dest_img_path, or return bytes of preprocessed image
        """
        if self.need_prep:
            img = self._read(img_path=src_img_path)
            orig_img_format = img.format
            if self._lr_dest_size > 0:
                img = _prep_img_longside_resize(img=img, dest_size=self._lr_dest_size)
            if dest_img_path:
                with open(dest_img_path, 'wb') as f:
                    img.save(dest_img_path, format=orig_img_format)
                return b''
            else:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=orig_img_format)
                return img_bytes.getvalue()
        else:
            if dest_img_path:
                shutil.copyfile(src_img_path, dest_img_path)
                return b''
            else:
                with open(src_img_path, 'rb') as f:
                    return f.read()

    def prep_pbs(self, attrs: mirpb.MetadataAttributes, image_annotations: mirpb.SingleImageAnnotations,
                 gt_annotations: mirpb.SingleImageAnnotations) -> None:
        if self._lr_dest_size > 0:
            _prep_pbs_longside_resize(attrs=attrs,
                                      image_annotations=image_annotations,
                                      gt_annotations=gt_annotations,
                                      dest_size=self._lr_dest_size)
