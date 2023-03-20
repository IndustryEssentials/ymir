import request from '@/utils/request'

/** prediction service */
/**
 * get prediction
 * @export
 * @param {number} id prediction id
 */
export function getPrediction(id: number) {
  return request.get(`predictions/${id}`)
}

/**
 * @description get predictions by query
 * @export
 * @param {YParams.PredictionsQuery}
 */
export function getPredictions({ pid, state, startTime, endTime, visible = true, offset = 0, limit = 10, desc = true }: YParams.PredictionsQuery) {
  return request.get('predictions/', {
    params: {
      project_id: pid,
      state,
      offset,
      limit,
      is_desc: desc,
      visible,
      start_time: startTime,
      end_time: endTime,
    },
  })
}

/**
 * @description batch task: hide predictions
 * @export
 * @param {string} action
 * @param {number} pid
 * @param {number[]} [ids=[]]
 */
export function batchAct(action: string, pid: number, ids: number[] = []) {
  return request.post(`/predictions/batch`, {
    project_id: pid,
    operations: ids.map((id) => ({ id, action })),
  })
}

/**
 * @description evalution between gt and prediction annotations by prediction
 * @export
 * @param {YParams.EvaluationParams} { pid, predictionId, iou, averageIou, confidence, ck, curve }
 */
export function evaluate({ pid, predictionId, iou, averageIou, confidence, ck, curve }: YParams.EvaluationParams) {
  return request.post(`/predictions/evaluation`, {
    project_id: pid,
    prediction_ids: [predictionId],
    confidence_threshold: confidence,
    iou_threshold: iou,
    require_average_iou: averageIou,
    main_ck: ck,
    need_pr_curve: curve,
  })
}
