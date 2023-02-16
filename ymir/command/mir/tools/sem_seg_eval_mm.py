from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import pycocotools.mask

from mir.protos import mir_command_pb2 as mirpb


# protected: semantic segmentation evaluation
def _mir_mean_iou(prediction: mirpb.SingleTaskAnnotations, ground_truth: mirpb.SingleTaskAnnotations,
                  class_ids: List[int],
                  assets_metadata: Optional[mirpb.MirMetadatas]) -> mirpb.SegmentationMetrics:
    dts = _aggregate_imagewise_annotations(task_annotations=prediction,
                                           assets_metadata=assets_metadata,
                                           class_ids=class_ids)
    gts = _aggregate_imagewise_annotations(task_annotations=ground_truth,
                                           assets_metadata=assets_metadata,
                                           class_ids=class_ids)
    all_acc, acc, iou, macc, miou = self._mean_iou(dts, gts, len(class_ids), 255, -1)
    order_to_class_id = dict(zip(range(len(class_ids)), class_ids))
    metrics = mirpb.SegmentationMetrics()
    metrics.aAcc = all_acc
    metrics.Acc.update({order_to_class_id[idx]: value for idx, value in enumerate(acc)})
    metrics.IoU.update({order_to_class_id[idx]: value for idx, value in enumerate(iou)})
    metrics.mAcc = macc
    metrics.mIoU = miou
    return metrics


def _aggregate_imagewise_annotations(task_annotations: mirpb.SingleTaskAnnotations,
                                     assets_metadata: mirpb.MirMetadatas,
                                     class_ids: List[int]) -> Dict[str, np.ndarray]:
    """
    annotations: self._gts or self._dts
    """
    class_id_to_order = dict(zip(class_ids, range(len(class_ids))))
    asset_ids = self._asset_ids

    asset_id_to_masks = {}

    for asset_id in asset_ids:
        if not self._assets_metadata:
            raise ValueError('assets_metadata is required for segmentation evaluation')
        asset_metadata = self._assets_metadata[asset_id]
        height, width = asset_metadata.height, asset_metadata.width
        # use 255 as a special class, which will be ignored upon evaluation
        img = np.ones(shape=(height, width), dtype=np.uint8) * 255
        for class_id in class_ids:
            for annotation in annotations[(asset_id, class_id)]:
                img[self.decode_mir_mask(annotation, height, width) == 1] = class_id_to_order[class_id]
        asset_id_to_masks[asset_id] = img
    return asset_id_to_masks


def _mean_iou(
    self,
    dts: List[np.ndarray],
    gts: List[np.ndarray],
    num_classes: int,
    ignore_index: int,
    nan_to_num: Optional[int] = None,
) -> List:
    (
        total_area_intersect,
        total_area_union,
        total_area_dt,
        total_area_gt,
    ) = self._total_intersect_and_union(dts, gts, num_classes, ignore_index)
    all_acc = np.nansum(total_area_intersect) / np.nansum(total_area_gt)
    acc = total_area_intersect / total_area_gt
    iou = total_area_intersect / total_area_union
    macc = np.nanmean(acc)
    miou = np.nanmean(iou)
    ret_metrics = [all_acc, acc, iou, macc, miou]
    if nan_to_num is not None:
        ret_metrics = [np.nan_to_num(metric, nan=nan_to_num) for metric in ret_metrics]
    return ret_metrics


def _intersect_and_union(
    self,
    dt: np.ndarray,
    gt: np.ndarray,
    num_classes: int,
    ignore_index: Optional[int],
) -> Tuple:
    mask = gt != ignore_index
    dt = dt[mask]
    gt = gt[mask]
    intersect = dt[dt == gt]
    area_intersect, _ = np.histogram(intersect, bins=np.arange(num_classes + 1))
    area_dt, _ = np.histogram(dt, bins=np.arange(num_classes + 1))
    area_gt, _ = np.histogram(gt, bins=np.arange(num_classes + 1))
    area_union = area_dt + area_gt - area_intersect
    return area_intersect, area_union, area_dt, area_gt


def _total_intersect_and_union(
    self,
    dts: List[np.ndarray],
    gts: List[np.ndarray],
    num_classes: int,
    ignore_index: int,
) -> Tuple:
    total_area_intersect = np.zeros((num_classes,), dtype=float)  # type: ignore
    total_area_union = np.zeros((num_classes,), dtype=float)  # type: ignore
    total_area_dt = np.zeros((num_classes,), dtype=float)  # type: ignore
    total_area_gt = np.zeros((num_classes,), dtype=float)  # type: ignore
    for dt, gt in zip(dts, gts):
        area_intersect, area_union, area_dt, area_gt = self._intersect_and_union(
            dt,
            gt,
            num_classes,
            ignore_index,
        )
        total_area_intersect += area_intersect
        total_area_union += area_union
        total_area_dt += area_dt
        total_area_gt += area_gt
    return total_area_intersect, total_area_union, total_area_dt, total_area_gt


def decode_mir_mask(annotation: Dict, height: float, width: float) -> np.ndarray:
    coco_segmentation: dict
    if annotation.get('mask'):
        coco_segmentation = {"counts": annotation["mask"], "size": [height, width]}
    elif annotation.get('polygon'):
        coco_segmentation = pycocotools.mask.frPyObjects(
            [[i for point in annotation["polygon"] for i in (point.x, point.y)]], height, width)[0]
    else:
        raise ValueError("Unsupported coco segmentation format")

    return pycocotools.mask.decode(coco_segmentation)


# public: general
def evaluate(prediction: mirpb.SingleTaskAnnotations, ground_truth: mirpb.SingleTaskAnnotations,
             config: mirpb.EvaluateConfig, assets_metadata: Optional[mirpb.MirMetadatas]) -> mirpb.Evaluation:
    evaluation = mirpb.Evaluation()
    evaluation.config.CopyFrom(config)

    evaluation.dataset_evaluation.segmentation_metrics.CopyFrom(
        _mir_mean_iou(prediction=prediction,
                      ground_truth=ground_truth,
                      assets_metadata=assets_metadata,
                      class_ids=config.class_ids))

    evaluation.state = mirpb.EvaluationState.ES_READY
    return evaluation