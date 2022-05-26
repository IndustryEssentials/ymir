from typing import Any, Iterator, List, Optional, Set, Tuple

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids, mir_storage_ops, revs_parser
from pkg_resources import yield_lines


def _tvt_type_from_str(typ: str) -> Optional[mirpb.TvtType]:
    str_to_typ = {
        'tr': mirpb.TvtType.TvtTypeTraining,
        'va': mirpb.TvtType.TvtTypeValidation,
        'te': mirpb.TvtType.TvtTypeTest,
    }
    return str_to_typ[typ] if typ else None


class MirDataReader:
    def __init__(self, mir_root: str, typ_rev_tid: revs_parser.TypRevTid, assets_location: str,
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
        self._assets_location = assets_location
        self._tvt_type = _tvt_type_from_str(typ_rev_tid.typ)
        self._asset_ids = [asset_id for asset_id in self._mir_metadatas.attributes.keys()]
        self._asset_ids.sort()
        self._class_ids = class_ids

    def read_single(self) -> Iterator[Tuple[str, mirpb.MetadataAttributes, List[mirpb.Annotation]]]:
        for asset_id in self._asset_ids:
            attr = self._mir_metadatas.attributes[asset_id]
            if self._tvt_type and attr.asset_type != self._tvt_type:
                continue  # if tvt type mismatch, continue

            annotations = []
            image_annotations = self._task_annotations.image_annotations.get(asset_id, None)
            if image_annotations:
                for annotation in image_annotations.annotations:
                    if class_ids and annotation.class_id in class_ids:
                        annotations.append(annotation)
            yield (asset_id, attr, annotations)
