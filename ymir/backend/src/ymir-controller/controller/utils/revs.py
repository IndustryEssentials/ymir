from typing import List

from proto import backend_pb2


def join_tvt_branch_tid(branch_id: str, tvt_type: str = None, tid: str = None) -> str:
    if not branch_id:
        raise RuntimeError('branch_id is required')
    ret = branch_id
    if tvt_type:
        ret = ':'.join([tvt_type, ret])
    if tid:
        ret = '@'.join([ret, tid])
    return ret


def build_tvt_dataset_id(tvt_dataset_id: str) -> backend_pb2.TaskReqTraining.TrainingDatasetType:
    _prefix_to_tvt = {
        'tr': backend_pb2.TvtTypeTraining,
        'va': backend_pb2.TvtTypeValidation,
        'te': backend_pb2.TvtTypeTest,
    }
    dataset_type = backend_pb2.TaskReqTraining.TrainingDatasetType()
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


def join_tvt_dataset_id(tvt_type: backend_pb2.TvtType, dataset_id: str) -> str:
    _tvt_to_prefix = {
        backend_pb2.TvtTypeUnknown: '',
        backend_pb2.TvtTypeTraining: 'tr:',
        backend_pb2.TvtTypeValidation: 'va:',
        backend_pb2.TvtTypeTest: 'te:',
    }
    return ''.join([_tvt_to_prefix[tvt_type], dataset_id])


def build_src_revs(in_src_revs: List[str], his_tid: str = None) -> str:
    # joined by ";", if his_rev is set, will be added to the first in_src_rev.
    first_src_rev = join_tvt_branch_tid(branch_id=in_src_revs[0], tid=his_tid)
    return ";".join([first_src_rev] + in_src_revs[1:])
