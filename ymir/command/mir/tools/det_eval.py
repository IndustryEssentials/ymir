from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

import numpy as np

from mir.tools import mir_storage_ops, revs_parser
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.protos import mir_command_pb2 as mirpb


class MirCoco:
    def __init__(self,
                 mir_metadatas: mirpb.MirMetadatas,
                 mir_annotations: mirpb.MirAnnotations,
                 mir_keywords: mirpb.MirKeywords,
                 conf_thr: float,
                 as_gt: bool,
                 asset_ids: Iterable[str] = None) -> None:
        """
        creates MirCoco instance

        Args:
            mir_metadatas (mirpb.MirMetadatas): metadatas
            mir_annotations (mirpb.MirAnnotations): annotations
            mir_keywords (mirpb.MirKeywords): keywords
            conf_thr (float): lower bound of annotation confidence score
            as_gt (bool): if false, use preds in mir_annotations and mir_keywords, if true, use gt
            asset_ids (Iterable[str]): asset ids you want to include in MirCoco instance, None means include all
        """
        task_annotations = mir_annotations.ground_truth if as_gt else mir_annotations.task_annotations[
            mir_annotations.head_task_id]
        keyword_to_idx = mir_keywords.gt_idx if as_gt else mir_keywords.pred_idx

        if len(mir_metadatas.attributes) == 0:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='no assets in evaluated dataset')
        if len(task_annotations.image_annotations) == 0:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_NO_ANNOTATIONS,
                                  error_message='no annotations in evaluated dataset')

        # ordered list of asset / image ids
        self._ordered_asset_ids = sorted(asset_ids or mir_metadatas.attributes.keys())
        # key: asset id, value: index in `self._ordered_asset_ids`
        self._asset_id_to_ordered_idxes = {asset_id: idx for idx, asset_id in enumerate(self._ordered_asset_ids)}
        # ordered list of class / category ids
        self._ordered_class_ids = sorted(list(keyword_to_idx.cis.keys()))
        self._ck_idx: Dict[str, mirpb.AssetAnnoIndex] = {key: value for key, value in mir_keywords.ck_idx.items()}

        self.img_cat_to_annotations: Dict[Tuple[int, int], List[dict]] = defaultdict(list)
        annos = self._get_annotations(single_task_annotations=task_annotations,
                                      asset_idxes=self.get_asset_idxes(),
                                      class_ids=self.get_class_ids(),
                                      conf_thr=None if as_gt else conf_thr)
        for anno in annos:
            self.img_cat_to_annotations[anno['asset_idx'], anno['class_id']].append(anno)

        self._task_annotations = task_annotations

    @property
    def ck_idx(self) -> Dict[str, mirpb.AssetAnnoIndex]:
        return self._ck_idx

    @property
    def asset_id_to_ordered_idxes(self) -> Dict[str, int]:
        return self._asset_id_to_ordered_idxes

    def _get_annotations(self, single_task_annotations: mirpb.SingleTaskAnnotations, asset_idxes: List[int],
                         class_ids: List[int], conf_thr: Optional[float]) -> List[dict]:
        """
        get all annotations list for asset ids and class ids

        if asset_idxes and class_ids provided, only returns filtered annotations

        Args:
            single_task_annotations (mirpb.SingleTaskAnnotations): annotations
            asset_idxes (List[int]): asset ids, if not provided, returns annotations for all images
            class_ids (List[int]): class ids, if not provided, returns annotations for all classe
            conf_thr (float): confidence threshold of bbox, set to None if you want all annotations

        Returns:
            a list of annotations and asset ids
            each element is a dict, and has following keys and values:
                asset_id: str, image / asset id
                asset_idx: int, position of asset id in `self.get_asset_ids()`
                id: int, id for a single annotation
                class_id: int, category / class id
                area: int, area of bbox
                bbox: List[int], bounding box, xywh
                score: float, confidence of bbox
                iscrowd: always 0 because mir knows nothing about it
        """
        result_annotations_list: List[dict] = []

        if not asset_idxes:
            asset_idxes = self.get_asset_idxes()

        annotation_idx = 1
        for asset_idx in asset_idxes:
            asset_id = self._ordered_asset_ids[asset_idx]
            if asset_id not in single_task_annotations.image_annotations:
                continue

            single_image_annotations = single_task_annotations.image_annotations[asset_id]
            for annotation in single_image_annotations.annotations:
                if class_ids and annotation.class_id not in class_ids:
                    continue
                if conf_thr is not None and annotation.score < conf_thr:
                    continue

                annotation_dict = {
                    'asset_id': asset_id,
                    'asset_idx': asset_idx,
                    'id': annotation_idx,
                    'class_id': annotation.class_id,
                    'area': annotation.box.w * annotation.box.h,
                    'bbox': [annotation.box.x, annotation.box.y, annotation.box.w, annotation.box.h],
                    'score': annotation.score,
                    'iscrowd': 0,
                    'ignore': 0,
                    'cm': {},  # key: (iou_thr_idx, maxDet), value: (ConfusionMatrixType, linked pb_index_id)
                    'pb_index_id': annotation.index,
                }
                result_annotations_list.append(annotation_dict)

                annotation_idx += 1

        return result_annotations_list

    def get_asset_ids(self) -> List[str]:
        return self._ordered_asset_ids

    def get_asset_idxes(self) -> List[int]:
        return list(range(len(self._ordered_asset_ids)))

    def get_class_ids(self) -> List[int]:
        return self._ordered_class_ids


class CocoDetEval:
    def __init__(self, coco_gt: MirCoco, coco_dt: MirCoco, params: 'Params' = None, asset_ids: Iterable[str] = None):
        self.evalImgs: list = []  # per-image per-category evaluation results [KxAxI] elements
        self.eval: dict = {}  # accumulated evaluation results
        self.params = params or Params()  # parameters
        self.stats: np.ndarray = np.zeros(1)  # result summarization
        self.ious: dict = {
        }  # key: (asset id, class id), value: ious ndarray of ith dt (sorted by score, desc) and jth gt
        self.params.catIds = coco_gt.get_class_ids()

        if asset_ids:
            self.params.imgIdxes = sorted([coco_gt.asset_id_to_ordered_idxes[x] for x in asset_ids])
            # gt for eval, key: (img_idx, cat_idx), value: annos list
            self._gts = self.filter_img_cat_to_annotations(img_cat_to_annotations=coco_gt.img_cat_to_annotations,
                                                           img_idxes=self.params.imgIdxes)
            # dt for eval, key: (img_idx, cat_idx), value: annos list
            self._dts = self.filter_img_cat_to_annotations(img_cat_to_annotations=coco_dt.img_cat_to_annotations,
                                                           img_idxes=self.params.imgIdxes)
        else:
            self.params.imgIdxes = coco_gt.get_asset_idxes()
            self._gts = defaultdict(list, coco_gt.img_cat_to_annotations)
            self._dts = defaultdict(list, coco_dt.img_cat_to_annotations)

        self._coco_gt = coco_gt
        self._coco_dt = coco_dt

    @classmethod
    def filter_img_cat_to_annotations(cls, img_cat_to_annotations: Dict[Tuple[int, int], List[dict]],
                                      img_idxes: List[int]) -> Dict[Tuple[int, int], List[dict]]:
        return defaultdict(list, {k: v for k, v in img_cat_to_annotations.items() if k[0] in img_idxes and len(v) > 0})

    def evaluate(self) -> None:
        '''
        Run per image evaluation on given images and store results (a list of dict) in self.evalImgs

        Returns: None
        SideEffects:
            self.params.catIds / imgIdxes: duplicated class and asset ids will be removed
            self.params.maxDets: will be sorted
            self.ious: will be cauculated
            self.evalImgs: will be cauculated
        '''
        self.params.maxDets.sort()
        p = self.params

        # loop through images, area range, max detection number
        catIds = p.catIds

        # self.ious: key: (img_idx, class_id), value: ious ndarray of len(dts) * len(gts)
        self.ious = {(imgIdx, catId): self.computeIoU(imgIdx, catId) for imgIdx in p.imgIdxes for catId in catIds}

        maxDet = p.maxDets[-1]
        self.evalImgs = [
            self.evaluateImg(imgIdx, catId, areaRng, maxDet) for catId in catIds for areaRng in p.areaRng
            for imgIdx in p.imgIdxes
        ]

    def computeIoU(self, imgIdx: int, catId: int) -> Union[np.ndarray, list]:
        """
        compute ious of detections and ground truth boxes of single image and class /category

        Args:
            imgIdx (int): asset / image ordered idx
            catId (int): category / class id

        Returns:
            ious ndarray of detections and ground truth boxes of single image and category
            ious[i][j] means the iou i-th detection (sorted by score, desc) and j-th ground truth box
        """
        gt = self._gts[imgIdx, catId]
        dt = self._dts[imgIdx, catId]
        if len(gt) == 0 and len(dt) == 0:
            return []

        # sort dt by score, desc
        inds = np.argsort([-d['score'] for d in dt], kind='mergesort')
        dt = [dt[i] for i in inds]
        if len(dt) > self.params.maxDets[-1]:
            dt = dt[0:self.params.maxDets[-1]]

        g_boxes = [g['bbox'] for g in gt]
        d_boxes = [d['bbox'] for d in dt]

        iscrowd = [int(o.get('iscrowd', 0)) for o in gt]
        # compute iou between each dt and gt region
        # ious: matrix of len(d_boxes) * len(g_boxes)
        #   ious[i][j]: iou of d_boxes[i] and g_boxes[j]
        ious = self._iou(d_boxes=d_boxes, g_boxes=g_boxes, iscrowd=iscrowd)
        return ious

    @classmethod
    def _iou(cls, d_boxes: List[List[int]], g_boxes: List[List[int]], iscrowd: List[int]) -> np.ndarray:
        def _single_iou(d_box: List[int], g_box: List[int], iscrowd: int) -> float:
            """ box: xywh """
            i_w = min(d_box[2] + d_box[0], g_box[2] + g_box[0]) - max(d_box[0], g_box[0])
            if i_w <= 0:
                return 0
            i_h = min(d_box[3] + d_box[1], g_box[3] + g_box[1]) - max(d_box[1], g_box[1])
            if i_h <= 0:
                return 0
            i_area = i_w * i_h
            u_area = d_box[2] * d_box[3] + g_box[2] * g_box[3] - i_area if not iscrowd else d_box[2] * d_box[3]
            return i_area / u_area

        ious = np.zeros((len(d_boxes), len(g_boxes)), dtype=np.double)
        for d_idx, d_box in enumerate(d_boxes):
            for g_idx, g_box in enumerate(g_boxes):
                ious[d_idx, g_idx] = _single_iou(d_box, g_box, iscrowd[g_idx])
        return ious

    def evaluateImg(self, imgIdx: int, catId: int, aRng: Any, maxDet: int) -> Optional[dict]:
        '''
        perform evaluation for single category and image

        Args:
            imgIdx (int): image / asset ordered index
            catId (int): category / class id
            aRng (List[float]): area range (lower and upper bound)
            maxDet (int):

        Returns:
            dict (single image results)
        '''
        gt = self._gts[imgIdx, catId]
        dt = self._dts[imgIdx, catId]
        if len(gt) == 0 and len(dt) == 0:
            return None

        for g in gt:
            if g['ignore'] or (g['area'] < aRng[0] or g['area'] > aRng[1]):
                g['_ignore'] = 1
            else:
                g['_ignore'] = 0

        # sort dt highest score first, sort gt ignore last
        gtind = np.argsort([g['_ignore'] for g in gt], kind='mergesort')
        gt = [gt[i] for i in gtind]
        dtind = np.argsort([-d['score'] for d in dt], kind='mergesort')
        dt = [dt[i] for i in dtind[0:maxDet]]
        iscrowd = [int(o['iscrowd']) for o in gt]
        # load computed ious
        ious = self.ious[imgIdx, catId][:, gtind] if len(self.ious[imgIdx, catId]) > 0 else self.ious[imgIdx, catId]

        p = self.params
        T = len(p.iouThrs)
        G = len(gt)
        D = len(dt)
        gtm = np.zeros((T, G))  # gtm[i, j]: dt annotation id matched by j-th gt in i-th iou thr, iouThrs x gts
        dtm = np.zeros((T, D))  # dtm[i, j]: gt annotation id matched by j-th dt in i-th iou thr, iouThrs x dets
        gtIg = np.array([g['_ignore'] for g in gt])  # gt ignore
        dtIg = np.zeros((T, D))  # dt ignore
        if not len(ious) == 0:
            for tind, t in enumerate(p.iouThrs):
                for gind, g in enumerate(gt):
                    g['cm'][tind, maxDet] = (mirpb.ConfusionMatrixType.FN, -1)  # default gt is FN, unless matched.
                    if gtIg[gind]:
                        g['cm'][tind, maxDet] = (mirpb.ConfusionMatrixType.IGNORED, -1)
                for dind, d in enumerate(dt):
                    d['cm'][tind, maxDet] = (mirpb.ConfusionMatrixType.FP, -1)  # default dt is FP, unless matched.
                    # information about best match so far (m=-1 -> unmatched)
                    iou = min([t, 1 - 1e-10])
                    m = -1  # best matched gind for current dind, -1 for unmatch
                    for gind, g in enumerate(gt):
                        # if this gt already matched, and not a crowd, continue
                        if gtm[tind, gind] > 0 and not iscrowd[gind]:
                            continue
                        # if dt matched to reg gt, and on ignore gt, stop
                        if m > -1 and gtIg[m] == 0 and gtIg[gind] == 1:
                            break
                        # continue to next gt unless better match made
                        if ious[dind, gind] < iou:
                            continue
                        # if match successful and best so far, store appropriately
                        iou = ious[dind, gind]
                        m = gind
                    # if match made store id of match for both dt and gt
                    if m == -1:
                        continue
                    dtIg[tind, dind] = gtIg[m]
                    dtm[tind, dind] = gt[m]['id']
                    gtm[tind, m] = d['id']
                    gt[m]['cm'][tind, maxDet] = (mirpb.ConfusionMatrixType.MTP, d['pb_index_id'])
                    d['cm'][tind, maxDet] = (mirpb.ConfusionMatrixType.TP, gt[m]['pb_index_id'])
        # set unmatched detections outside of area range to ignore
        a = np.array([d['area'] < aRng[0] or d['area'] > aRng[1] for d in dt]).reshape((1, len(dt)))
        dtIg = np.logical_or(dtIg, np.logical_and(dtm == 0, np.repeat(a, T, 0)))
        for dind, d in enumerate(dt):
            if dtIg[tind, dind]:
                gt_pb_index_id = d['cm'][tind, maxDet][1]
                d['cm'][tind, maxDet] = (mirpb.ConfusionMatrixType.IGNORED, gt_pb_index_id)
        # store results for given image and category
        return {
            'image_id': imgIdx,
            'category_id': catId,
            'aRng': aRng,
            'maxDet': maxDet,
            'dtIds': [d['id'] for d in dt],
            'gtIds': [g['id'] for g in gt],
            'dtMatches': dtm,
            'gtMatches': gtm,
            'dtScores': [d['score'] for d in dt],
            'gtIgnore': gtIg,
            'dtIgnore': dtIg,
        }

    def accumulate(self, p: 'Params' = None) -> None:
        '''
        Accumulate per image evaluation results and store the result in self.eval
        :param p: input params for evaluation
        :return: None
        '''
        if not self.evalImgs:
            raise ValueError('Please run evaluate() first')

        # allows input customized parameters
        if p is None:
            p = self.params
        T = len(p.iouThrs)
        R = len(p.recThrs)
        K = len(p.catIds)
        A = len(p.areaRng)
        M = len(p.maxDets)
        precision = -np.ones((T, R, K, A, M))  # -1 for the precision of absent categories
        recall = -np.ones((T, K, A, M))
        scores = -np.ones((T, R, K, A, M))
        all_tps = np.zeros((T, K, A, M))
        all_fps = np.zeros((T, K, A, M))
        all_fns = np.zeros((T, K, A, M))

        # create dictionary for future indexing
        catIds = self.params.catIds
        setK: set = set(catIds)
        setA: Set[tuple] = set(map(tuple, self.params.areaRng))
        setM: set = set(self.params.maxDets)
        setI: set = set(self.params.imgIdxes)
        # get inds to evaluate
        k_list = [n for n, k in enumerate(p.catIds) if k in setK]
        m_list = [m for n, m in enumerate(p.maxDets) if m in setM]
        a_list = [n for n, a in enumerate(map(lambda x: tuple(x), p.areaRng)) if a in setA]
        i_list = [n for n, i in enumerate(p.imgIdxes) if i in setI]
        I0 = len(self.params.imgIdxes)
        A0 = len(self.params.areaRng)
        # retrieve E at each category, area range, and max number of detections
        for k, k0 in enumerate(k_list):
            Nk = k0 * A0 * I0
            for a, a0 in enumerate(a_list):
                Na = a0 * I0
                for m, maxDet in enumerate(m_list):
                    E = [self.evalImgs[Nk + Na + i] for i in i_list]
                    E = [e for e in E if e is not None]
                    if len(E) == 0:
                        continue
                    dtScores = np.concatenate([e['dtScores'][0:maxDet] for e in E])
                    if len(dtScores) == 0:
                        continue

                    # different sorting method generates slightly different results.
                    # mergesort is used to be consistent as Matlab implementation.
                    inds = np.argsort(-dtScores, kind='mergesort')
                    dtScoresSorted = dtScores[inds]

                    dtm = np.concatenate([e['dtMatches'][:, 0:maxDet] for e in E], axis=1)[:, inds]
                    dtIg = np.concatenate([e['dtIgnore'][:, 0:maxDet] for e in E], axis=1)[:, inds]
                    gtIg = np.concatenate([e['gtIgnore'] for e in E])
                    npig = np.count_nonzero(gtIg == 0)
                    if npig == 0:
                        continue

                    tps = np.logical_and(dtm, np.logical_not(dtIg))  # iouThrs x dts
                    fps = np.logical_and(np.logical_not(dtm), np.logical_not(dtIg))  # iouThrs x dts
                    tp_sum = np.cumsum(tps, axis=1).astype(dtype=float)
                    fp_sum = np.cumsum(fps, axis=1).astype(dtype=float)

                    all_tps[:, k, a, m] = tp_sum[:, -1]
                    all_fps[:, k, a, m] = fp_sum[:, -1]
                    all_fns[:, k, a, m] = npig - all_tps[:, k, a, m]

                    for t, (tp, fp) in enumerate(zip(tp_sum, fp_sum)):
                        tp = np.array(tp)
                        fp = np.array(fp)
                        nd = len(tp)
                        rc = tp / npig
                        pr = tp / (fp + tp + np.spacing(1))
                        q = np.zeros((R, ))
                        ss = np.zeros((R, ))

                        if nd:
                            recall[t, k, a, m] = rc[-1]
                        else:
                            recall[t, k, a, m] = 0

                        # numpy is slow without cython optimization for accessing elements
                        # use python array gets significant speed improvement
                        pr = pr.tolist()
                        q = q.tolist()

                        for i in range(nd - 1, 0, -1):
                            if pr[i] > pr[i - 1]:
                                pr[i - 1] = pr[i]

                        inds = np.searchsorted(rc, p.recThrs, side='left')
                        try:
                            for ri, pi in enumerate(inds):
                                q[ri] = pr[pi]
                                ss[ri] = dtScoresSorted[pi]
                        except Exception:
                            pass
                        precision[t, :, k, a, m] = np.array(q)
                        scores[t, :, k, a, m] = np.array(ss)

        self.eval = {
            'params': p,
            'counts': [T, R, K, A, M],
            'precision': precision,
            'recall': recall,
            'scores': scores,
            'all_fps': all_fps,
            'all_tps': all_tps,
            'all_fns': all_fns,
        }

    def get_evaluation_result(self, area_ranges_index: int, max_dets_index: int) -> mirpb.SingleDatasetEvaluation:
        if not self.eval:
            raise ValueError('Please run accumulate() first')

        evaluation_result = mirpb.SingleDatasetEvaluation()
        evaluation_result.conf_thr = self.params.confThr

        # iou evaluations
        for iou_thr_index, iou_thr in enumerate(self.params.iouThrs):
            iou_evaluation = self._get_iou_evaluation_result(area_ranges_index=area_ranges_index,
                                                             max_dets_index=max_dets_index,
                                                             iou_thr_index=iou_thr_index)
            evaluation_result.iou_evaluations[f"{iou_thr:.2f}"].CopyFrom(iou_evaluation)

        # average evaluation
        evaluation_result.iou_averaged_evaluation.CopyFrom(
            self._get_iou_evaluation_result(area_ranges_index=area_ranges_index, max_dets_index=max_dets_index))

        return evaluation_result

    def _get_iou_evaluation_result(self,
                                   area_ranges_index: int,
                                   max_dets_index: int,
                                   iou_thr_index: int = None) -> mirpb.SingleIouEvaluation:
        iou_evaluation = mirpb.SingleIouEvaluation()

        # ci evaluations: category / class ids
        for class_id_index, class_id in enumerate(self.params.catIds):
            ee = self._get_evaluation_element(iou_thr_index, class_id_index, area_ranges_index, max_dets_index)
            iou_evaluation.ci_evaluations[class_id].CopyFrom(ee)
        # class average
        ee = self._get_evaluation_element(iou_thr_index, None, area_ranges_index, max_dets_index)
        iou_evaluation.ci_averaged_evaluation.CopyFrom(ee)

        return iou_evaluation

    def _get_evaluation_element(self, iou_thr_index: Optional[int], class_id_index: Optional[int],
                                area_ranges_index: int, max_dets_index: int) -> mirpb.SingleEvaluationElement:
        def _get_tp_tn_or_fn(iou_thr_index: Optional[int], class_id_index: Optional[int], area_ranges_index: int,
                             max_dets_index: int, array: np.ndarray) -> int:
            """
            extract tp, tn and fn from `array`

            `array` comes from self.eval's all_tps, all_tns and all_fns, they all have the same structure:
                iouThrs x catIds x aRngs x maxDets
            """
            if iou_thr_index is not None:
                array = array[[iou_thr_index]]
            if class_id_index is not None:
                array = array[:, class_id_index, area_ranges_index, max_dets_index]
            else:
                array = np.sum(array[:, :, area_ranges_index, max_dets_index], axis=1)
            return int(array[0])

        ee = mirpb.SingleEvaluationElement()

        # average precision
        # precision dims: iouThrs * recThrs * catIds * areaRanges * maxDets
        precisions: np.ndarray = self.eval['precision']
        if iou_thr_index is not None:
            precisions = precisions[[iou_thr_index]]
        if class_id_index is not None:
            precisions = precisions[:, :, class_id_index, area_ranges_index, max_dets_index]
        else:
            precisions = precisions[:, :, :, area_ranges_index, max_dets_index]
        precisions[precisions <= -1] = 0
        ee.ap = np.mean(precisions) if len(precisions) > 0 else -1

        # average recall
        # recall dims: iouThrs * catIds * areaRanges * maxDets
        recalls: np.ndarray = self.eval['recall']
        if iou_thr_index is not None:
            recalls = recalls[[iou_thr_index]]
        if class_id_index is not None:
            recalls = recalls[:, class_id_index, area_ranges_index, max_dets_index]
        else:
            recalls = recalls[:, :, area_ranges_index, max_dets_index]
        recalls[recalls <= -1] = 0
        ee.ar = np.mean(recalls) if len(recalls) > 0 else -1

        # true positive
        ee.tp = _get_tp_tn_or_fn(iou_thr_index=iou_thr_index,
                                 class_id_index=class_id_index,
                                 area_ranges_index=area_ranges_index,
                                 max_dets_index=max_dets_index,
                                 array=self.eval['all_tps'])

        # false positive
        ee.fp = _get_tp_tn_or_fn(iou_thr_index=iou_thr_index,
                                 class_id_index=class_id_index,
                                 area_ranges_index=area_ranges_index,
                                 max_dets_index=max_dets_index,
                                 array=self.eval['all_fps'])

        # false negative
        ee.fn = _get_tp_tn_or_fn(iou_thr_index=iou_thr_index,
                                 class_id_index=class_id_index,
                                 area_ranges_index=area_ranges_index,
                                 max_dets_index=max_dets_index,
                                 array=self.eval['all_fns'])

        # pr curve
        if self.params.need_pr_curve:
            # self.eval['precision'] dims: iouThrs * recThrs * catIds * areaRanges * maxDets
            # precisions dims: iouThrs * recThrs * catIds
            precisions = self.eval['precision'][:, :, :, area_ranges_index, max_dets_index]
            scores = self.eval['scores'][:, :, :, area_ranges_index, max_dets_index]

            # TODO: hotfix, need to test with 3rd party pr curve result
            precisions = np.maximum(0, precisions)
            scores = np.maximum(0, scores)

            # from dims: iouThrs * recThrs * catIds
            # to dims: recThrs * catIds
            if iou_thr_index is not None:
                precisions = precisions[iou_thr_index, :, :]
                scores = scores[iou_thr_index, :, :]
            else:
                precisions = np.mean(precisions, axis=0)
                scores = np.mean(scores, axis=0)

            # from dims: recThrs * catIds
            # to dims: recThrs
            if class_id_index is not None:
                precisions = precisions[:, class_id_index]
                scores = scores[:, class_id_index]
            else:
                precisions = np.mean(precisions, axis=1)
                scores = np.mean(scores, axis=1)

            for recall_thr_index, recall_thr in enumerate(self.params.recThrs):
                pr_point = mirpb.FloatPoint(x=recall_thr, y=precisions[recall_thr_index], z=scores[recall_thr_index])
                ee.pr_curve.append(pr_point)

        return ee

    def summarize(self) -> None:
        '''
        Compute and display summary metrics for evaluation results.
        Note this functin can *only* be applied on the default parameter setting
        '''
        def _summarize(ap: int = 1, iouThr: float = None, areaRng: str = 'all', maxDets: int = 100) -> float:
            p = self.params

            aind = [i for i, aRng in enumerate(p.areaRngLbl) if aRng == areaRng]  # areaRanges index
            mind = [i for i, mDet in enumerate(p.maxDets) if mDet == maxDets]  # maxDets index
            if ap == 1:
                # dimension of precision: [TxRxKxAxM] iouThrs * recThrs * catIds * areaRanges * maxDets
                s = self.eval['precision']
                # IoU
                if iouThr is not None:
                    t = np.where(iouThr == p.iouThrs)[0]
                    s = s[t]
                s = s[:, :, :, aind, mind]
            else:
                # dimension of recall: [TxKxAxM] iouThrs * catIds * areaRanges * maxDets
                s = self.eval['recall']
                if iouThr is not None:
                    t = np.where(iouThr == p.iouThrs)[0]
                    s = s[t]
                s = s[:, :, aind, mind]
            if len(s[s > -1]) == 0:
                mean_s = -1
            else:
                mean_s = np.mean(s[s > -1])
            return mean_s

        def _summarizeDets() -> np.ndarray:
            stats = np.zeros((3, ))
            stats[0] = _summarize(1)
            stats[1] = _summarize(1, iouThr=.5, maxDets=self.params.maxDets[-1])
            stats[2] = _summarize(1, iouThr=.75, maxDets=self.params.maxDets[-1])
            return stats

        if not self.eval:
            raise Exception('Please run accumulate() first')
        self.stats = _summarizeDets()

    def write_confusion_matrix(self, iou_thr_index: int, maxDets: int) -> None:
        gt_annotation = self._coco_gt._task_annotations
        dt_annotation = self._coco_dt._task_annotations
        cm_key = (iou_thr_index, maxDets)
        for imgIdx in self.params.imgIdxes:
            for catId in self.params.catIds:
                gt = self._gts[imgIdx, catId]
                if len(gt):
                    gt_img_annotation = gt_annotation.image_annotations[gt[0]['asset_id']]
                    pb_idx_to_anno = {anno.index: anno for anno in gt_img_annotation.annotations}
                    for g in gt:
                        if not g.get('cm', {}).get(cm_key, None):
                            continue
                        cm_tuple = g['cm'][cm_key]
                        anno = pb_idx_to_anno[g['pb_index_id']]
                        anno.cm, anno.det_link_id = cm_tuple[0], cm_tuple[1]

                dt = self._dts[imgIdx, catId]
                if len(dt):
                    dt_img_annotation = dt_annotation.image_annotations[dt[0]['asset_id']]
                    pb_idx_to_anno = {anno.index: anno for anno in dt_img_annotation.annotations}
                    for d in dt:
                        if not d.get('cm', {}).get(cm_key, None):
                            continue
                        cm_tuple = d['cm'][cm_key]
                        anno = pb_idx_to_anno[d['pb_index_id']]
                        anno.cm, anno.det_link_id = cm_tuple[0], cm_tuple[1]


class Params:
    def __init__(self) -> None:
        self.iouType = 'bbox'
        self.catIds: List[int] = []
        self.imgIdxes: List[int] = []
        # np.arange causes trouble.  the data point on arange is slightly larger than the true value
        self.iouThrs = np.linspace(.5, 0.95, int(np.round((0.95 - .5) / .05)) + 1, endpoint=True)  # iou threshold
        self.recThrs = np.linspace(.0, 1.00, int(np.round((1.00 - .0) / .01)) + 1, endpoint=True)  # recall threshold
        self.maxDets = [100]  # only one maxDet, origin: [1, 10, 100]
        # [[0**2, 1e5**2], [0**2, 32**2], [32**2, 96**2], [96**2, 1e5**2]]  # area range
        self.areaRng: List[list] = [[0**2, 1e5**2]]  # use all.
        self.areaRngLbl = ['all', 'small', 'medium', 'large']  # area range label
        self.confThr = 0.3  # confidence threshold
        self.need_pr_curve = False
        self.calc_confusion_matrix = False


def _det_evaluate(mir_dts: Dict[str, MirCoco], mir_gt_and_id: Tuple[str, MirCoco],
                  config: mirpb.EvaluateConfig) -> Dict[str, mirpb.SingleDatasetEvaluation]:
    if config.conf_thr < 0 or config.conf_thr > 1:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid conf_thr')

    mir_gt_id, mir_gt = mir_gt_and_id

    params = Params()
    params.confThr = config.conf_thr
    params.iouThrs = _get_ious_array(config.iou_thrs_interval)
    params.need_pr_curve = config.need_pr_curve
    params.calc_confusion_matrix = config.calc_confusion_matrix
    if params.calc_confusion_matrix and params.iouThrs.size != 1:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_CAN_NOT_CALC_CONFUSION_MATRIX,
                              error_message='single iou thr is needed if calc_confusion_matrix')

    area_ranges_index = 0  # area range: 'all'
    max_dets_index = len(params.maxDets) - 1  # last max det number

    sdes: Dict[str, mirpb.SingleDatasetEvaluation] = {}
    for mir_dt_id, mir_dt in mir_dts.items():
        evaluator = CocoDetEval(coco_gt=mir_gt, coco_dt=mir_dt, params=params)
        evaluator.evaluate()
        if params.calc_confusion_matrix:
            iou_thr_index = 0  # single iou thr only.
            evaluator.write_confusion_matrix(iou_thr_index=iou_thr_index, maxDets=params.maxDets[max_dets_index])
        evaluator.accumulate()

        single_dataset_evaluation = evaluator.get_evaluation_result(area_ranges_index=area_ranges_index,
                                                                    max_dets_index=max_dets_index)
        single_dataset_evaluation.conf_thr = config.conf_thr

        # evaluate for asset_ids for each ck main and ck sub
        for ck_main, ck_main_assets_and_sub in mir_dt.ck_idx.items():
            # ck main
            evaluator = CocoDetEval(coco_gt=mir_gt,
                                    coco_dt=mir_dt,
                                    params=params,
                                    asset_ids=ck_main_assets_and_sub.asset_annos.keys())
            evaluator.evaluate()
            evaluator.accumulate()
            ste = evaluator.get_evaluation_result(
                area_ranges_index=area_ranges_index,
                max_dets_index=max_dets_index).iou_averaged_evaluation.ci_averaged_evaluation
            single_dataset_evaluation.iou_averaged_evaluation.ck_evaluations[ck_main].total.CopyFrom(ste)

            # ck sub
            for ck_sub, ck_sub_assets in ck_main_assets_and_sub.sub_indexes.items():
                evaluator = CocoDetEval(coco_gt=mir_gt,
                                        coco_dt=mir_dt,
                                        params=params,
                                        asset_ids=ck_sub_assets.key_ids.keys())
                evaluator.evaluate()
                evaluator.accumulate()
                ste = evaluator.get_evaluation_result(
                    area_ranges_index=area_ranges_index,
                    max_dets_index=max_dets_index).iou_averaged_evaluation.ci_averaged_evaluation
                single_dataset_evaluation.iou_averaged_evaluation.ck_evaluations[ck_main].sub[ck_sub].CopyFrom(ste)

        single_dataset_evaluation.gt_dataset_id = mir_gt_id
        single_dataset_evaluation.pred_dataset_id = mir_dt_id
        sdes[mir_dt_id] = single_dataset_evaluation
    return sdes


def _get_ious_array(iou_thrs_str: str) -> np.ndarray:
    iou_thrs = [float(v) for v in iou_thrs_str.split(':')]
    if len(iou_thrs) == 3:
        iou_thr_from, iou_thr_to, iou_thr_step = iou_thrs
    elif len(iou_thrs) == 1:
        iou_thr_from, iou_thr_to, iou_thr_step = iou_thrs[0], iou_thrs[0], 0
    else:
        raise ValueError(f"invalid iou thrs str: {iou_thrs_str}")
    for thr in [iou_thr_from, iou_thr_to, iou_thr_step]:
        if thr < 0 or thr > 1:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='invalid iou_thr_from, iou_thr_to or iou_thr_step')
    if iou_thr_from > iou_thr_to:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='invalid iou_thr_from or iou_thr_to')

    if iou_thr_to == iou_thr_from:
        return np.array([iou_thr_from])
    return np.linspace(start=iou_thr_from,
                       stop=iou_thr_to,
                       num=int(np.round((iou_thr_to - iou_thr_from) / iou_thr_step)),
                       endpoint=False)


def det_evaluate(
    mir_root: str,
    rev_tid: revs_parser.TypRevTid,
    conf_thr: float,
    iou_thrs: str,
    need_pr_curve: bool = False,
    calc_confusion_matrix: bool = False,
) -> Tuple[mirpb.Evaluation, mirpb.MirAnnotations]:
    mir_metadatas: mirpb.MirMetadatas
    mir_annotations: mirpb.MirAnnotations
    mir_keywords: mirpb.MirKeywords
    mir_metadatas, mir_annotations, mir_keywords = mir_storage_ops.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=rev_tid.rev,
        mir_task_id=rev_tid.tid,
        ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS, mirpb.MirStorage.MIR_KEYWORDS])

    return det_evaluate_with_pb(mir_metadatas=mir_metadatas,
                                mir_annotations=mir_annotations,
                                mir_keywords=mir_keywords,
                                rev_tid=rev_tid,
                                conf_thr=conf_thr,
                                iou_thrs=iou_thrs,
                                need_pr_curve=need_pr_curve,
                                calc_confusion_matrix=calc_confusion_matrix)


def det_evaluate_with_pb(
    mir_metadatas: mirpb.MirMetadatas,
    mir_annotations: mirpb.MirAnnotations,
    mir_keywords: mirpb.MirKeywords,
    rev_tid: revs_parser.TypRevTid,
    conf_thr: float,
    iou_thrs: str,
    need_pr_curve: bool = False,
    calc_confusion_matrix: bool = False,
) -> Tuple[mirpb.Evaluation, mirpb.MirAnnotations]:
    mir_gt = MirCoco(mir_metadatas=mir_metadatas,
                     mir_annotations=mir_annotations,
                     mir_keywords=mir_keywords,
                     conf_thr=conf_thr,
                     as_gt=True)
    mir_dt = MirCoco(mir_metadatas=mir_metadatas,
                     mir_annotations=mir_annotations,
                     mir_keywords=mir_keywords,
                     conf_thr=conf_thr,
                     as_gt=False)

    evaluation = mirpb.Evaluation()
    evaluation.config.conf_thr = conf_thr
    evaluation.config.iou_thrs_interval = iou_thrs
    evaluation.config.need_pr_curve = need_pr_curve
    evaluation.config.calc_confusion_matrix = calc_confusion_matrix
    evaluation.config.gt_dataset_id = rev_tid.rev_tid
    evaluation.config.pred_dataset_ids.append(rev_tid.rev_tid)

    dataset_evaluations = _det_evaluate(mir_dts={rev_tid.rev_tid: mir_dt},
                                        mir_gt_and_id=(rev_tid.rev_tid, mir_gt),
                                        config=evaluation.config)

    for dt_id, dse in dataset_evaluations.items():
        evaluation.dataset_evaluations[dt_id].CopyFrom(dse)

    return (evaluation, mir_annotations)
