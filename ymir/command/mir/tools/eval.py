from collections import defaultdict
import copy
from typing import Any, List, Optional, Set, Union

import numpy as np
from pycocotools import mask as maskUtils

from mir.tools import mir_storage_ops, revs_parser
from mir.protos import mir_command_pb2 as mirpb


class MirCoco:
    def __init__(self, mir_root: str, rev_tid: revs_parser.TypRevTid) -> None:
        m: mirpb.MirMetadatas
        a: mirpb.MirAnnotations
        k: mirpb.MirKeywords
        m, a, k, = mir_storage_ops.MirStorageOps.load_multiple_storages(mir_root=mir_root,
                                                                        mir_branch=rev_tid.rev,
                                                                        mir_task_id=rev_tid.tid,
                                                                        ms_list=[
                                                                            mirpb.MirStorage.MIR_METADATAS,
                                                                            mirpb.MirStorage.MIR_ANNOTATIONS,
                                                                            mirpb.MirStorage.MIR_KEYWORDS,
                                                                        ])
        self._mir_metadatas = m
        self._mir_annotations = a
        self._mir_keywords = k

        # ordered list of asset / image ids
        self._ordered_asset_ids = sorted(list(self._mir_metadatas.attributes.keys()))
        # key: asset id, value: index in `self._ordered_asset_ids`
        self._asset_id_to_ordered_idxes = {asset_id: idx for idx, asset_id in enumerate(self._ordered_asset_ids)}
        # ordered list of class / category ids
        self._ordered_class_ids = sorted(list(self._mir_keywords.index_predifined_keyids.keys()))

    @property
    def mir_metadatas(self) -> mirpb.MirMetadatas:
        return self._mir_metadatas

    @property
    def mir_annotations(self) -> mirpb.MirAnnotations:
        return self._mir_annotations

    def get_annotations(self,
                        asset_idxes: List[int] = [],
                        class_ids: List[int] = [],
                        conf_thr: float = 0) -> List[dict]:
        """
        get all annotations list for asset ids and class ids

        if asset_idxes and class_ids provided, only returns filtered annotations

        Args:
            asset_idxes (List[int]): asset ids, if not provided, returns annotations for all images
            class_ids (List[int]): class ids, if not provided, returns annotations for all classe
            conf_thr (float): confidence threshold of bbox

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

        single_task_annotations = self._mir_annotations.task_annotations[self._mir_annotations.head_task_id]
        if not asset_idxes:
            asset_idxes = self.get_asset_idxes()

        for asset_idx in asset_idxes:
            asset_id = self._ordered_asset_ids[asset_idx]
            if asset_id not in single_task_annotations.image_annotations:
                continue

            single_image_annotations = single_task_annotations.image_annotations[asset_id]
            for annotation in single_image_annotations.annotations:
                if class_ids and annotation.class_id not in class_ids:
                    continue
                if annotation.score < conf_thr:
                    continue

                annotation_dict = {
                    'asset_id': asset_id,
                    'asset_idx': asset_idx,
                    'id': annotation.index + 1,  # annotation id starts from 1, so + 1 is needed
                    'class_id': annotation.class_id,
                    'area': annotation.box.w * annotation.box.h,
                    'bbox': [annotation.box.x, annotation.box.y, annotation.box.w, annotation.box.h],
                    'score': annotation.score,
                    'iscrowd': 0,
                }
                result_annotations_list.append(annotation_dict)

        return result_annotations_list

    def get_asset_ids(self) -> List[str]:
        return self._ordered_asset_ids

    def get_asset_idxes(self) -> List[int]:
        return list(range(len(self._ordered_asset_ids)))

    def get_class_ids(self) -> List[int]:
        return self._ordered_class_ids


class MirEval:
    def __init__(self, coco_gt: MirCoco, coco_dt: MirCoco, params: 'Params' = None):
        self.cocoGt = coco_gt  # ground truth COCO API
        self.cocoDt = coco_dt  # detections COCO API
        self.evalImgs: list = []  # per-image per-category evaluation results [KxAxI] elements
        self.eval: dict = {}  # accumulated evaluation results
        self._gts: dict = defaultdict(list)  # gt for evaluation
        self._dts: dict = defaultdict(list)  # dt for evaluation
        self.params = params or Params()  # parameters
        self._paramsEval: Params = Params()  # parameters for evaluation
        self.stats: np.ndarray = np.zeros(1)  # result summarization
        self.ious: dict = {
        }  # key: (asset id, class id), value: ious ndarray of ith dt (sorted by score, desc) and jth gt
        self.params.imgIdxes = list(range(len(coco_gt.get_asset_ids())))
        self.params.catIds = coco_dt.get_class_ids()

    def _prepare(self) -> None:
        '''
        Prepare self._gts and self._dts for evaluation based on params

        SideEffects:
            created and filled self._gts and self._dts; changed self.evalImgs and self.eval
        '''
        if self.params.useCats:  # TODO: shall i remove this?
            gts = self.cocoGt.get_annotations(asset_idxes=self.params.imgIdxes,
                                              class_ids=self.params.catIds,
                                              conf_thr=self.params.confThr)
            dts = self.cocoDt.get_annotations(asset_idxes=self.params.imgIdxes,
                                              class_ids=self.params.catIds,
                                              conf_thr=self.params.confThr)
        else:
            gts = self.cocoGt.get_annotations(asset_idxes=self.params.imgIdxes, conf_thr=self.params.confThr)
            dts = self.cocoDt.get_annotations(asset_idxes=self.params.imgIdxes, conf_thr=self.params.confThr)

        # set ignore flag
        for gt in gts:
            gt['ignore'] = gt['ignore'] if 'ignore' in gt else 0
            gt['ignore'] = 'iscrowd' in gt and gt['iscrowd']

        # for each element in self._gts and self._dts:
        #   key: (asset_idx, class_id)
        #   value: {'asset_idx': int, 'id': int, 'class_id': int, 'bbox': int tuple of xywh, 'score': float}
        for gt in gts:
            self._gts[gt['asset_idx'], gt['class_id']].append(gt)
        for dt in dts:
            self._dts[dt['asset_idx'], dt['class_id']].append(dt)

    def evaluate(self) -> None:
        '''
        Run per image evaluation on given images and store results (a list of dict) in self.evalImgs

        Returns: None
        SideEffects:
            self.params.catIds / imgIdxes: duplicated class and asset ids will be removed
            self.params.maxDets: will be sorted
            self.ious: will be cauculated
            self.evalImgs: will be cauculated
            self._paramsEval: deep copied from self.params
        '''
        p = self.params
        p.imgIdxes = list(np.unique(p.imgIdxes))
        if p.useCats:
            p.catIds = list(np.unique(p.catIds))
        p.maxDets = sorted(p.maxDets)
        self.params = p

        self._prepare()
        # loop through images, area range, max detection number
        catIds = p.catIds if p.useCats else [-1]

        # self.ious: key: (img_idx, class_id), value: ious ndarray of len(dts) * len(gts)
        self.ious = {(imgId, catId): self.computeIoU(imgId, catId) for imgId in p.imgIdxes for catId in catIds}

        maxDet = p.maxDets[-1]
        self.evalImgs = [
            self.evaluateImg(imgIdx, catId, areaRng, maxDet) for catId in catIds for areaRng in p.areaRng
            for imgIdx in p.imgIdxes
        ]
        self._paramsEval = copy.deepcopy(self.params)  # pragma: ignore type

    def computeIoU(self, imgIdx: int, catId: int) -> Union[np.ndarray, list]:
        """
        compute ious of detections and ground truth boxes of single image and class /category

        Args:
            imgIdx (int): asset / image ordered idx
            catId (int): category / class id, if self.params.useCats is False, catId will be ignored

        Returns:
            ious ndarray of detections and ground truth boxes of single image and category
            ious[i][j] means the iou i-th detection (sorted by score, desc) and j-th ground truth box
        """
        p = self.params
        if p.useCats:
            gt = self._gts[imgIdx, catId]
            dt = self._dts[imgIdx, catId]
        else:
            # if not useCats, gt and dt set to annotations for the same imgIdx and ALL cat ids
            gt = [_ for cId in p.catIds for _ in self._gts[imgIdx, cId]]
            dt = [_ for cId in p.catIds for _ in self._dts[imgIdx, cId]]
        if len(gt) == 0 and len(dt) == 0:
            return []

        # sort dt by score, desc
        inds = np.argsort([-d['score'] for d in dt], kind='mergesort')
        dt = [dt[i] for i in inds]
        if len(dt) > p.maxDets[-1]:
            dt = dt[0:p.maxDets[-1]]

        g_boxes = [g['bbox'] for g in gt]
        d_boxes = [d['bbox'] for d in dt]

        iscrowd = [int(o.get('iscrowd', 0)) for o in gt]
        # compute iou between each dt and gt region
        # ious: matrix of len(d_boxes) * len(g_boxes)
        #   ious[i][j]: iou of d_boxes[i] and g_boxes[j]
        ious = maskUtils.iou(d_boxes, g_boxes, iscrowd)
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
        p = self.params
        if p.useCats:
            gt = self._gts[imgIdx, catId]
            dt = self._dts[imgIdx, catId]
        else:
            gt = [_ for cId in p.catIds for _ in self._gts[imgIdx, cId]]
            dt = [_ for cId in p.catIds for _ in self._dts[imgIdx, cId]]
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

        T = len(p.iouThrs)
        G = len(gt)
        D = len(dt)
        gtm = np.zeros((T, G))  # gtm[i, j]: dt annotation id matched by j-th gt in i-th iou thr, iouThrs x gts
        dtm = np.zeros((T, D))  # dtm[i, j]: gt annotation id matched by j-th dt in i-th iou thr, iouThrs x dets
        gtIg = np.array([g['_ignore'] for g in gt])  # gt ignore
        dtIg = np.zeros((T, D))  # dt ignore
        if not len(ious) == 0:
            for tind, t in enumerate(p.iouThrs):
                for dind, d in enumerate(dt):
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
        # set unmatched detections outside of area range to ignore
        a = np.array([d['area'] < aRng[0] or d['area'] > aRng[1] for d in dt]).reshape((1, len(dt)))
        dtIg = np.logical_or(dtIg, np.logical_and(dtm == 0, np.repeat(a, T, 0)))
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
        print('Accumulating evaluation results...')
        if not self.evalImgs:
            print('Please run evaluate() first')
        # allows input customized parameters
        if p is None:
            p = self.params
        p.catIds = p.catIds if p.useCats == 1 else [-1]
        T = len(p.iouThrs)
        R = len(p.recThrs)
        K = len(p.catIds) if p.useCats else 1
        A = len(p.areaRng)
        M = len(p.maxDets)
        precision = -np.ones((T, R, K, A, M))  # -1 for the precision of absent categories
        recall = -np.ones((T, K, A, M))
        scores = -np.ones((T, R, K, A, M))
        all_tps = -np.ones((T, K, A, M))
        all_fps = -np.ones((T, K, A, M))
        all_fns = -np.ones((T, K, A, M))

        # create dictionary for future indexing
        _pe = self._paramsEval
        catIds = _pe.catIds if _pe.useCats else [-1]
        setK: set = set(catIds)
        setA: Set[tuple] = set(map(tuple, _pe.areaRng))
        setM: set = set(_pe.maxDets)
        setI: set = set(_pe.imgIdxes)
        # get inds to evaluate
        k_list = [n for n, k in enumerate(p.catIds) if k in setK]
        m_list = [m for n, m in enumerate(p.maxDets) if m in setM]
        a_list = [n for n, a in enumerate(map(lambda x: tuple(x), p.areaRng)) if a in setA]
        i_list = [n for n, i in enumerate(p.imgIdxes) if i in setI]
        I0 = len(_pe.imgIdxes)
        A0 = len(_pe.areaRng)
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

    def get_evaluation_result(self) -> mirpb.Evaluation:
        if not self.eval:
            raise ValueError('Please run accumulate() first')

        evaluation_result = mirpb.Evaluation()
        evaluation_result.conf_threshold = self.params.confThr

        # iou evaluations
        for iou_thr_index, iou_thr in enumerate(self.params.iouThrs):
            iou_evaluation = self._get_iou_evaluation_result(iou_thr_index=iou_thr_index)
            evaluation_result.iou_evaluations[str(iou_thr)].CopyFrom(iou_evaluation)

        # average evaluation
        evaluation_result.average_evaluation.CopyFrom(self._get_iou_evaluation_result())

        return evaluation_result

    def _get_iou_evaluation_result(self, iou_thr_index: int = None) -> mirpb.SingleIouEvaluation:
        iou_evaluation = mirpb.SingleIouEvaluation()

        # ci evaluations: category / class ids
        for class_id_index, class_id in enumerate(self.params.catIds):
            topic_evaluation = self._get_topic_evaluation_result(iou_thr_index, class_id_index)
            iou_evaluation.ci_evaluations[class_id].CopyFrom(topic_evaluation)

        return iou_evaluation

    def _get_topic_evaluation_result(self, iou_thr_index: Optional[int],
                                     class_id_index: int) -> mirpb.SingleTopicEvaluation:
        topic_evaluation = mirpb.SingleTopicEvaluation()

        # from _summarize
        area_ranges_index = 0  # area range: 'all'
        max_dets_index = len(self.params.maxDets) - 1  # last max det number

        # average precision
        # precision dims: iouThrs * recThrs * catIds * areaRanges * maxDets
        precisions: np.ndarray = self.eval['precision']
        if iou_thr_index is not None:
            precisions = precisions[[iou_thr_index]]
        if class_id_index is not None:
            precisions = precisions[:, :, class_id_index, area_ranges_index, max_dets_index]
        else:
            precisions = precisions[:, :, :, area_ranges_index, max_dets_index]
        precisions = precisions[precisions > -1]
        topic_evaluation.ap = np.mean(precisions) if len(precisions) > 0 else -1

        # average recall
        # recall dims: iouThrs * catIds * areaRanges * maxDets
        recalls: np.ndarray = self.eval['recall']
        if iou_thr_index is not None:
            recalls = recalls[[iou_thr_index]]
        if class_id_index is not None:
            recalls = recalls[:, class_id_index, area_ranges_index, max_dets_index]
        else:
            recalls = recalls[:, :, area_ranges_index, max_dets_index]
        recalls = recalls[recalls > -1]
        topic_evaluation.ar = np.mean(recalls) if len(recalls) > 0 else -1

        # true positive
        all_tps = self.eval['all_tps']
        if iou_thr_index is not None:
            all_tps = all_tps[[iou_thr_index]]
        if class_id_index is not None:
            all_tps = all_tps[:, class_id_index, area_ranges_index, max_dets_index]
        else:
            all_tps = all_tps[:, :, area_ranges_index, max_dets_index]
        topic_evaluation.tp = int(all_tps[0])

        # false positive
        all_fps = self.eval['all_fps']
        if iou_thr_index is not None:
            all_fps = all_fps[[iou_thr_index]]
        if class_id_index is not None:
            all_fps = all_fps[:, class_id_index, area_ranges_index, max_dets_index]
        else:
            all_fps = all_fps[:, :, area_ranges_index, max_dets_index]
        topic_evaluation.fp = int(all_fps[0])

        # TODO: false negative

        # pr curve
        if iou_thr_index is not None and class_id_index is not None:
            precisions = self.eval['precision'][iou_thr_index, :, class_id_index, area_ranges_index, max_dets_index]
            for recall_thr_index, recall_thr in enumerate(self.params.recThrs):
                pr_point = mirpb.FloatPoint(x=recall_thr, y=precisions[recall_thr_index])
                topic_evaluation.pr_curve.append(pr_point)

        return topic_evaluation

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
            stats = np.zeros((12, ))
            stats[0] = _summarize(1)
            stats[1] = _summarize(1, iouThr=.5, maxDets=self.params.maxDets[2])
            stats[2] = _summarize(1, iouThr=.75, maxDets=self.params.maxDets[2])
            stats[3] = _summarize(1, areaRng='small', maxDets=self.params.maxDets[2])
            stats[4] = _summarize(1, areaRng='medium', maxDets=self.params.maxDets[2])
            stats[5] = _summarize(1, areaRng='large', maxDets=self.params.maxDets[2])
            stats[6] = _summarize(0, maxDets=self.params.maxDets[0])
            stats[7] = _summarize(0, maxDets=self.params.maxDets[1])
            stats[8] = _summarize(0, maxDets=self.params.maxDets[2])
            stats[9] = _summarize(0, areaRng='small', maxDets=self.params.maxDets[2])
            stats[10] = _summarize(0, areaRng='medium', maxDets=self.params.maxDets[2])
            stats[11] = _summarize(0, areaRng='large', maxDets=self.params.maxDets[2])
            return stats

        if not self.eval:
            raise Exception('Please run accumulate() first')
        self.stats = _summarizeDets()


class Params:
    def __init__(self) -> None:
        self.iouType = 'bbox'
        self.catIds: List[int] = []
        self.imgIdxes: List[int] = []
        # np.arange causes trouble.  the data point on arange is slightly larger than the true value
        self.iouThrs = np.linspace(.5, 0.95, int(np.round((0.95 - .5) / .05)) + 1, endpoint=True)  # iou threshold
        self.recThrs = np.linspace(.0, 1.00, int(np.round((1.00 - .0) / .01)) + 1, endpoint=True)  # recall threshold
        self.maxDets = [1, 10, 100]
        self.areaRng: List[list] = [[0**2, 1e5**2], [0**2, 32**2], [32**2, 96**2], [96**2, 1e5**2]]  # area range
        self.areaRngLbl = ['all', 'small', 'medium', 'large']  # area range label
        self.useCats = 1  # 1: use categories, 0: treat all categories as one
        self.confThr = 0.3  # confidence threshold
        # useSegm is deprecated
        self.useSegm = None
