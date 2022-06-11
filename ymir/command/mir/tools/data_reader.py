from typing import Any, Iterator, Set, Tuple

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops, revs_parser


class MirDataReader:
    def __init__(self, mir_root: str, typ_rev_tid: revs_parser.TypRevTid, asset_ids: Set[str],
                 class_ids: Set[int]) -> None:
        self._mir_root = mir_root
        self._typ_rev_tid = typ_rev_tid
        self._asset_ids = asset_ids
        self._class_ids = class_ids

    def __enter__(self) -> Any:
        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_metadatas, mir_annotations = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch=self._typ_rev_tid.rev,
            mir_task_id=self._typ_rev_tid.tid,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS])

        self._mir_metadatas = mir_metadatas
        self._task_annotations = mir_annotations.task_annotations[mir_annotations.head_task_id]
        if not self._asset_ids:
            self._asset_ids = {asset_id for asset_id in self._mir_metadatas.attributes.keys()}

        return self

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        pass

    def read(self) -> Iterator[Tuple[str, mirpb.MetadataAttributes, mirpb.SingleImageAnnotations]]:
        for asset_id, attributes in self._mir_metadatas.attributes.items():
            if asset_id not in self._asset_ids:
                continue

            image_annotations = self._task_annotations.image_annotations.get(asset_id, None)
            filtered_image_annotations = mirpb.SingleImageAnnotations()

            if image_annotations:
                # need to keep cks and image_quality
                filtered_image_annotations.CopyFrom(image_annotations)
                del filtered_image_annotations.annotations[:]

                for annotation in image_annotations.annotations:
                    if self._class_ids and annotation.class_id not in self._class_ids:
                        continue
                    filtered_image_annotations.annotations.append(annotation)

            yield (asset_id, attributes, filtered_image_annotations)
