import request from '@/utils/request'

/** prediction service */
/**
 * get dataset
 * @export
 * @param {number} id dataset id
 * @param {boolean} verbose for more infomation
 */
export function getPrediction(id: number, verbose: boolean) {
  return request.get(`predictions/${id}`, { params: { verbose } })
}

/**
 * @description get datasets by query
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
 * @description evalution between gt and prediction annotations by dataset
 * @export
 * @param {EvaluationParams} {
 *   pid, datasets, iou, averageIou, confidence, ck
 * }
 */
export function evaluate({ pid, datasets, iou, averageIou, confidence, ck, curve }: YParams.EvaluationParams) {
  return request.post(`/predictions/evaluation`, {
    project_id: pid,
    prediction_ids: datasets,
    confidence_threshold: confidence,
    iou_threshold: iou,
    require_average_iou: averageIou,
    main_ck: ck,
    need_pr_curve: curve,
  })
}
