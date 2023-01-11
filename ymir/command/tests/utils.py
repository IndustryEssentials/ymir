import os
import shutil
import subprocess
from typing import Any, Dict, List, Tuple, Type

from google.protobuf.json_format import MessageToDict, ParseDict
import yaml

from mir.commands.init import CmdInit
from mir.commands.checkout import CmdCheckout
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids, mir_storage_ops
from mir.tools.code import MirCode


def dir_test_root(sub_dirs: List[str]) -> str:
    return os.path.join("/tmp/mir_cmd_test", '/'.join(sub_dirs))


# check enviroment
def check_commands():
    """
    test if git command available
    """
    subprocess.run("git --version".split(" "), stdout=subprocess.DEVNULL)


# mir repo operations
def mir_repo_init(mir_root: str):
    return_code = CmdInit.run_with_args(mir_root=mir_root,
                                        label_storage_file=class_ids.ids_file_path(mir_root),
                                        empty_rev='')
    assert return_code == MirCode.RC_OK, "init failed"


def mir_repo_create_branch(mir_root: str, branch_name: str):
    assert len(branch_name) > 0
    return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=branch_name, branch_new=True)
    assert return_code == MirCode.RC_OK, "create branch failed"


def mir_repo_checkout(mir_root: str, branch_name: str):
    assert len(branch_name) > 0
    return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=branch_name, branch_new=False)
    assert return_code == MirCode.RC_OK, "checkout commit failed"


def read_mir_pb(mir_root: str, mir_pb_type: Type):
    mir_pb_instance = mir_pb_type()
    with open(mir_root, "rb") as f:
        mir_pb_instance.ParseFromString(f.read())
    return mir_pb_instance


def remake_dirs(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def prepare_labels(mir_root: str, names: List[str]):
    labels: List[class_ids.SingleLabel] = []
    for idx, name in enumerate(names):
        components = name.split(',')
        labels.append(class_ids.SingleLabel(id=idx, name=components[0], aliases=components[1:]))
    label_storage = class_ids.LabelStorage(labels=labels)

    with open(class_ids.ids_file_path(mir_root=mir_root), 'w') as f:
        yaml.safe_dump(label_storage.dict(), f)


def diff_dicts(a_dict: dict, b_dict: dict, stack: list) -> None:
    if set(a_dict.keys()) != set(b_dict.keys()):
        raise ValueError(f"stack: {stack} keys mismatched\na: {sorted(a_dict.keys())}\nb: {sorted(b_dict.keys())}")
    for ka in a_dict:
        va = a_dict[ka]
        vb = b_dict[ka]
        diff_types(va, vb, stack=stack + [ka])
        if isinstance(va, dict):
            diff_dicts(a_dict=va, b_dict=vb, stack=stack + [ka])
        else:
            diff_others(a=va, b=vb, stack=stack + [ka])


def diff_types(a: Any, b: Any, stack: list) -> None:
    if not isinstance(a, type(b)) and not isinstance(b, type(a)):
        raise ValueError(f"stack: {stack} types mismatched: {type(a)} vs {type(b)}")


def diff_others(a: Any, b: Any, stack: list) -> None:
    if a != b:
        raise ValueError(f"stack: {stack}, other kind of values mismatched:\na: {a}\nb: {b}")


def convert_dict_str_keys_to_int(d: dict) -> None:
    if not isinstance(d, dict):
        return

    allkeys = list(d.keys())
    for k in allkeys:
        v = d[k]
        if isinstance(k, str) and k.isdigit():
            d[int(k)] = v
            del d[k]
        if isinstance(v, dict):
            convert_dict_str_keys_to_int(v)
        elif isinstance(v, list):
            for vv in v:
                convert_dict_str_keys_to_int(vv)


def prepare_mir_branch(mir_root: str, assets_and_keywords: Dict[str, Tuple[List[int], List[str]]], size: int,
                       branch_name_and_task_id: str, commit_msg: str):
    mir_annotations = mirpb.MirAnnotations()
    mir_metadatas = mirpb.MirMetadatas()

    dict_metadatas: Dict[str, Any] = {'attributes': {}}
    for asset_id in assets_and_keywords:
        dict_metadatas["attributes"][asset_id] = generate_attribute_for_asset(size, size)
    ParseDict(dict_metadatas, mir_metadatas)

    image_annotations = {}
    image_cks = {}
    class_ids_set = set()
    for asset_idx, (asset_id, keywords_pair) in enumerate(assets_and_keywords.items()):
        image_annotations[asset_id] = generate_annotations_for_asset(type_ids=keywords_pair[0],
                                                                      x=100,
                                                                      y=(asset_idx + 1) * 100)
        image_cks[asset_id] = {'cks': keywords_pair[1]}
        class_ids_set.update(keywords_pair[0])
    pred = {
        'task_id': branch_name_and_task_id,
        'type': mirpb.ObjectType.OT_DET_BOX,
        "image_annotations": image_annotations,
        "eval_class_ids": list(class_ids_set),
        'task_class_ids': list(class_ids_set),
    }
    gt = {
        'task_id': branch_name_and_task_id,
        'type': mirpb.ObjectType.OT_DET_BOX,
        "image_annotations": image_annotations,
        'task_class_ids': list(class_ids_set),
    }
    dict_annotations = {
        "prediction": pred,
        'ground_truth': gt,
        'image_cks': image_cks,
    }
    ParseDict(dict_annotations, mir_annotations)

    task = mir_storage_ops.create_task(task_type=mirpb.TaskTypeMining,
                                       task_id=branch_name_and_task_id,
                                       message=commit_msg)
    mir_storage_ops.MirStorageOps.save_and_commit(mir_root=mir_root,
                                                  mir_branch=branch_name_and_task_id,
                                                  his_branch='master',
                                                  mir_datas={
                                                      mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                      mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                  },
                                                  task=task)


def generate_attribute_for_asset(width: int, height: int, tvt_type: int = mirpb.TvtTypeUnknown) -> dict:
    if tvt_type == mirpb.TvtTypeUnknown:
        return {'asset_type': 'AssetTypeImageJpeg', 'width': width, 'height': height, 'image_channels': 3}
    else:
        return {
            'asset_type': 'AssetTypeImageJpeg',
            'width': width,
            'height': height,
            'image_channels': 3,
            "tvt_type": mirpb.TvtType.Name(tvt_type)
        }


def generate_annotations_for_asset(type_ids: List[int], x: int, y: int, cm: int = mirpb.ConfusionMatrixType.NotSet):
    annotations_list = []
    for idx, type_id in enumerate(type_ids):
        annotations_list.append({
            'class_id': type_id,
            'cm': cm,
            'det_link_id': -1,
            'box': {
                'x': idx * 100 + x,
                'y': y,
                'w': 50,
                'h': 50
            },
        })
    return {'boxes': annotations_list, 'img_class_ids': type_ids}
