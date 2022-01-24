import request from "@/utils/request"

/** dataset service */
/**
 *
 * @param {array[number]} id
 * @returns
 */
export function getDataset(id) {
  return request.get(`datasets/${id}`)
}

/**
 * @param {*} params
 * { name, type, start_time = 0, end_time = 0, offset = 0, limit = 10, is_desc = true, order_by = 1 }
 * @returns
 */
export function getDatasets(params) {
  return request.get("datasets/", { params })
}

export function batchDatasets(ids) {
  return request.get('datasets/batch', { params: { ids: ids.toString() }})
}

/**
 * get assets of dataset
 * @param {object} param0 fitler condition
 * @returns
 */
export function getAssetsOfDataset({
  id,
  keyword = null,
  offset = 0,
  limit = 20,
}) {
  return request.get(`datasets/${id}/assets`, {
    params: {
      keyword,
      offset,
      limit,
    },
  })
}

export function getAsset(id, hash) {
  return request.get(`datasets/${id}/assets/${hash}`)
}

/**
 * delete dataset
 * @param {number} id
 * @returns
 */
export function delDataset(id) {
  return request({
    method: "delete",
    url: `/datasets/${id}`,
  })
}

/**
 * create a dataset
 * @param {object} dataset
 * {
 *   "name": "string",
 *   "hash": "string",
 *   "type": 1,
 *   "predicates": "string",
 *   "asset_count": 0,
 *   "keyword_count": 0,
 *   "user_id": 0,
 *   "task_id": 0
 * }
 * @returns
 */
export function createDataset(dataset) {
  return request.post("/datasets/", dataset)
}

export function updateDataset(id, name) {
  return request({
    method: "patch",
    url: `/datasets/${id}`,
    data: {
      name,
    },
  })
}

export function getInternalDataset() {
  return request.get('/datasets/public')
}
