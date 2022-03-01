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
 * get dataset versions by group id
 * @param {number} group_id 
 * @returns 
 */
export function getDatasetVersions(group_id) {
  return request.get(`dataset_groups/${group_id}`)
}

/**
 * get datasets
 * @param {object} param1 {
 *   {number} project_id 
 *   {number} type task type
 *   {number} state dataset state
 *   {string} name dataset name
 *   {number} offset  query start
 *   {number} limit query count 
 * }
 * @returns 
 */
export function queryDatasets({ project_id, type, state, name, offset = 0, limit = 10 }) {
  return request.get("datasets/", { params: { project_id, type, state, name, offset, limit } })
}
/**
 * get dataset groups
 * @param {object} param1 {
 *   {number} project_id 
 *   {string} name dataset name
 *   {number} offset  query start
 *   {number} limit query count 
 * }
 * @returns 
 */
export function getDatasets(project_id, { name, offset = 0, limit = 10 }) {
  return request.get("dataset_groups/", { params: { project_id, name, offset, limit } })
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
