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
export function getPredictions({
  pid,
  state,
  startTime,
  endTime,
  visible = true,
  offset = 0,
  limit = 10,
  desc = true,
}: YParams.PredictionsQuery) {
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
 * batch getting dataset
 *
 * @export
 * @param {number} pid
 * @param {number[]} [ids=[]]
 * @param {boolean} ck
 */
export function batchPredictions(pid: number, ids: number[] = [], ck: boolean) {
  return request.get('predictions/batch', {
    params: {
      project_id: pid,
      ids: ids.toString(),
      ck,
    },
  })
}
