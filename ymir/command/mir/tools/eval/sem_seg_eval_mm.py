from collections import defaultdict
from typing import Any, Dict, List, Optional, OrderedDict, Tuple

import numpy as np
import pycocotools.mask

from mir.protos import mir_command_pb2 as mirpb
from mir.tools.eval.eval_utils import get_iou_thrs_array, write_semantic_confusion_matrix


_SEMANTIC_SEGMENTATION_BACKGROUND = 255


# protected: semantic segmentation evaluation
def _mir_mean_iou(
        prediction: mirpb.SingleTaskAnnotations, ground_truth: mirpb.SingleTaskAnnotations, class_ids: List[int],
        asset_id_to_hws: OrderedDict[str, Tuple[int, int]]) -> Tuple[mirpb.SegmentationMetrics, np.ndarray]:

    dts = _aggregate_imagewise_annotations(task_annotations=prediction,
                                           asset_id_to_hws=asset_id_to_hws,
                                           class_ids=class_ids)
    gts = _aggregate_imagewise_annotations(task_annotations=ground_truth,
                                           asset_id_to_hws=asset_id_to_hws,
                                           class_ids=class_ids)
    all_acc, acc, iou, macc, miou, image_class_iou = _mean_iou(dts=dts,
                                                               gts=gts,
                                                               num_classes=len(class_ids),
                                                               ignore_index=_SEMANTIC_SEGMENTATION_BACKGROUND,
                                                               nan_to_num=-1)
    order_to_class_id = dict(zip(range(len(class_ids)), class_ids))

    metrics = mirpb.SegmentationMetrics()
    metrics.aAcc = all_acc
    metrics.Acc.update({order_to_class_id[idx]: value for idx, value in enumerate(acc)})
    metrics.IoU.update({order_to_class_id[idx]: value for idx, value in enumerate(iou)})
    metrics.mAcc = macc
    metrics.mIoU = miou

    return metrics, image_class_iou


def _aggregate_imagewise_annotations(task_annotations: mirpb.SingleTaskAnnotations,
                                     asset_id_to_hws: OrderedDict[str, Tuple[int, int]],
                                     class_ids: List[int]) -> List[np.ndarray]:
    class_id_to_order = dict(zip(class_ids, range(len(class_ids))))

    image_annotations: List[np.ndarray] = []
    for asset_id, hw in asset_id_to_hws.items():
        # use 255 as a special class, which will be ignored upon evaluation
        img = np.ones(shape=hw, dtype=np.uint8) * _SEMANTIC_SEGMENTATION_BACKGROUND
        if asset_id not in task_annotations.image_annotations:
            image_annotations.append(img)
            continue

        for annotation in task_annotations.image_annotations[asset_id].boxes:
            if annotation.class_id not in class_ids:
                continue
            img[_decode_mir_mask(annotation, hw) == 1] = class_id_to_order[annotation.class_id]
        image_annotations.append(img)
    return image_annotations


# protected: calc mean iou
def _mean_iou(
    dts: List[np.ndarray],
    gts: List[np.ndarray],
    num_classes: int,
    ignore_index: int,
    nan_to_num: Optional[int] = None,
) -> List[Any]:
    """
    calc mean iou and associated metrics
    Returns:
        list of 5 elements: aAcc (float), Acc (ndarray), IoU (ndarray), mAcc (float), mIoU (float)
        Acc (ndarray): i-th element means Acc of i-th class
        IoU (ndarray): i-th element means IoU of i-th class
    """
    (
        total_area_intersect,
        total_area_union,
        _,
        total_area_gt,
        image_class_iou
    ) = _total_intersect_and_union(dts, gts, num_classes, ignore_index)
    all_acc = np.nansum(total_area_intersect) / np.nansum(total_area_gt)
    acc = total_area_intersect / total_area_gt
    iou = total_area_intersect / total_area_union
    macc = np.nanmean(acc)
    miou = np.nanmean(iou)
    ret_metrics = [all_acc, acc, iou, macc, miou, image_class_iou]
    if nan_to_num is not None:
        ret_metrics = [np.nan_to_num(metric, nan=nan_to_num) for metric in ret_metrics]
    return ret_metrics


def _intersect_and_union(
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
    dts: List[np.ndarray],
    gts: List[np.ndarray],
    num_classes: int,
    ignore_index: int,
) -> Tuple:
    total_area_intersect = np.zeros((num_classes,), dtype=float)
    total_area_union = np.zeros((num_classes,), dtype=float)
    total_area_dt = np.zeros((num_classes,), dtype=float)
    total_area_gt = np.zeros((num_classes,), dtype=float)
    image_class_iou = np.zeros((len(dts), num_classes), dtype=float)  # [i, j]: iou of i-th image and j-th class
    for asset_idx, (dt, gt) in enumerate(zip(dts, gts)):
        area_intersect, area_union, area_dt, area_gt = _intersect_and_union(
            dt,
            gt,
            num_classes,
            ignore_index,
        )
        total_area_intersect += area_intersect
        total_area_union += area_union
        total_area_dt += area_dt
        total_area_gt += area_gt
        image_class_iou[asset_idx, :] = area_intersect / area_union
    return total_area_intersect, total_area_union, total_area_dt, total_area_gt, image_class_iou


def _decode_mir_mask(annotation: mirpb.ObjectAnnotation, hw: Tuple[int, int]) -> np.ndarray:
    coco_segmentation: dict
    if annotation.type == mirpb.ObjectSubType.OST_SEG_MASK:
        coco_segmentation = {"counts": annotation.mask, "size": hw}
    elif annotation.type == mirpb.ObjectSubType.OST_SEG_POLYGON:
        coco_segmentation = pycocotools.mask.frPyObjects(
            [[i for point in annotation.polygon for i in (point.x, point.y)]], hw[0], hw[1])[0]
    else:
        raise ValueError(f"Unsupported object annotation sub type: {annotation.type}")

    return pycocotools.mask.decode(coco_segmentation)


# public: general
def evaluate(prediction: mirpb.SingleTaskAnnotations, ground_truth: mirpb.SingleTaskAnnotations,
             config: mirpb.EvaluateConfig, assets_metadata: mirpb.MirMetadatas) -> mirpb.Evaluation:
    evaluation = mirpb.Evaluation()
    evaluation.config.CopyFrom(config)

    asset_ids = sorted(prediction.image_annotations.keys() | ground_truth.image_annotations.keys())
    asset_id_to_hws: OrderedDict[str, Tuple[int, int]] = OrderedDict()
    for asset_id in asset_ids:
        if asset_id not in assets_metadata.attributes:
            continue
        asset_id_to_hws[asset_id] = (assets_metadata.attributes[asset_id].height,
                                     assets_metadata.attributes[asset_id].width)

    iou, image_class_iou = _mir_mean_iou(prediction=prediction,
                                         ground_truth=ground_truth,
                                         asset_id_to_hws=asset_id_to_hws,
                                         class_ids=list(config.class_ids))
    evaluation.dataset_evaluation.segmentation_metrics.CopyFrom(iou)

    # write cm
    if config.iou_thrs_interval:
        iou_thr = get_iou_thrs_array(config.iou_thrs_interval)[0]
        match_result: Dict[str, List[int]] = defaultdict(list)
        for i in range(len(asset_ids)):
            for j in range(len(config.class_ids)):
                if image_class_iou[i, j] >= iou_thr:
                    match_result[asset_ids[i]].append(config.class_ids[j])

        write_semantic_confusion_matrix(gt_annotations=ground_truth,
                                        pred_annotations=prediction,
                                        class_ids=list(config.class_ids),
                                        match_result=match_result)

    evaluation.state = mirpb.EvaluationState.ES_READY
    return evaluation
