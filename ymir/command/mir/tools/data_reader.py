from typing import Iterator, List, Set, Tuple

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops, revs_parser


class MirDataReader:
    def __init__(self, mir_root: str, typ_rev_tid: revs_parser.TypRevTid, asset_ids: Set[str],
                 class_ids: Set[int]) -> None:
        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_metadatas, mir_annotations = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=typ_rev_tid.rev,
            mir_task_id=typ_rev_tid.tid,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS])

        self._mir_metadatas = mir_metadatas
        self._task_annotations = mir_annotations.task_annotations[mir_annotations.head_task_id]
        self._asset_ids = asset_ids or {asset_id for asset_id in self._mir_metadatas.attributes.keys()}
        self._class_ids = class_ids

        self._empty_annotations_count = 0

    @property
    def empty_annotations_count(self) -> int:
        return self._empty_annotations_count

    def read(self) -> Iterator[Tuple[str, mirpb.MetadataAttributes, List[mirpb.Annotation]]]:
        self._empty_annotations_count = 0
        for asset_id, attributes in self._mir_metadatas.attributes.items():
            if asset_id not in self._asset_ids:
                continue

            annotations = []
            image_annotations = self._task_annotations.image_annotations.get(asset_id, None)
            if image_annotations:
                for annotation in image_annotations.annotations:
                    if not self._class_ids or annotation.class_id in self._class_ids:
                        annotations.append(annotation)

            if not annotations:
                self._empty_annotations_count += 1

            yield (asset_id, attributes, annotations)
