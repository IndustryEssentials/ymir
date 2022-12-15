from typing import List

from proto import backend_pb2
from mir.protos import mir_command_pb2 as mir_cmd_pb


def join_tvt_branch_tid(branch_id: str, tvt_type: str = None, tid: str = None) -> str:
    if not branch_id:
        raise RuntimeError('branch_id is required')
    ret = branch_id
    if tvt_type:
        ret = ':'.join([tvt_type, ret])
    if tid:
        ret = '@'.join([ret, tid])
    return ret


def build_tvt_dataset_id(tvt_dataset_id: str) -> backend_pb2.TrainingDatasetType:
    _prefix_to_tvt = {
        'tr': mir_cmd_pb.TvtTypeTraining,
        'va': mir_cmd_pb.TvtTypeValidation,
        'te': mir_cmd_pb.TvtTypeTest,
    }
    dataset_type = backend_pb2.TrainingDatasetType()
    split_data = tvt_dataset_id.split(':')
    if len(split_data) == 2:
        dataset_type.dataset_type = _prefix_to_tvt[split_data[0].lower()]
        dataset_type.dataset_id = split_data[1]
    elif len(split_data) == 1:
        dataset_type.dataset_type = backend_pb2.TvtTypeUnknown
        dataset_type.dataset_id = tvt_dataset_id
    else:
        raise RuntimeError("invalid tvt_dataset_id: {}".format(tvt_dataset_id))
    return dataset_type


def join_tvt_dataset_id(tvt_type: mir_cmd_pb.TvtType, dataset_id: str) -> str:
    _tvt_to_prefix = {
        mir_cmd_pb.TvtTypeUnknown: '',
        mir_cmd_pb.TvtTypeTraining: 'tr:',
        mir_cmd_pb.TvtTypeValidation: 'va:',
        mir_cmd_pb.TvtTypeTest: 'te:',
    }
    return ''.join([_tvt_to_prefix[tvt_type], dataset_id])


def build_src_revs(in_src_revs: List[str], his_tid: str = None) -> str:
    # joined by ";", if his_rev is set, will be added to the first in_src_rev.
    first_src_rev = join_tvt_branch_tid(branch_id=in_src_revs[0], tid=his_tid)
    return ";".join([first_src_rev] + in_src_revs[1:])
