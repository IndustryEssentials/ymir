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
        self._gt_annotations = mir_annotations.ground_truth
        self._image_cks = mir_annotations.image_cks
        if not self._asset_ids:
            self._asset_ids = {asset_id for asset_id in self._mir_metadatas.attributes.keys()}

        return self

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        pass

    def read(
        self
    ) -> Iterator[Tuple[str, mirpb.MetadataAttributes, mirpb.SingleImageAnnotations, mirpb.SingleImageAnnotations,
                        mirpb.SingleImageCks]]:
        image_annotations = self._task_annotations.image_annotations
        gt_annotations = self._gt_annotations.image_annotations
        for asset_id, attributes in self._mir_metadatas.attributes.items():
            if asset_id not in self._asset_ids:
                continue

            filtered_image_annotations = mirpb.SingleImageAnnotations()
            if asset_id in image_annotations:
                for annotation in image_annotations[asset_id].annotations:
                    if self._class_ids and annotation.class_id not in self._class_ids:
                        continue
                    filtered_image_annotations.annotations.append(annotation)

            filtered_gt_annotations = mirpb.SingleImageAnnotations()
            if asset_id in gt_annotations:
                for annotation in gt_annotations[asset_id].annotations:
                    if self._class_ids and annotation.class_id not in self._class_ids:
                        continue
                    filtered_gt_annotations.annotations.append(annotation)

            yield (asset_id, attributes, filtered_image_annotations, filtered_gt_annotations, self._image_cks[asset_id])
