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
export function getDatasetByGroup(group_id) {
  return request.get(`datasets/`, { params: { group_id, is_desc: false, limit: 10000 }})
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
export function getDatasetGroups(project_id, { name, offset = 0, limit = 10 }) {
  return request.get("dataset_groups/", { params: { project_id, name, offset, limit } })
}

export function batchDatasets(ids) {
  return request.get('datasets/batch', { params: { ids: ids.toString() } })
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
 * delete dataset
 * @param {number} id
 * @returns
 */
export function delDatasetGroup(id) {
  console.log('group id: ', id)
  return request({
    method: "delete",
    url: `/dataset_groups/${id}`,
  })
}

/**
 * import a dataset into project
 * @param {object} dataset
 * {
 *   {string} name
 *   {number} projectId
 *   {string} url
 *   {number} [datasetId]
 *   {string} [inputPath]
 *   {number} [strategy] default: 0
 * }
 * @returns
 */
export function createDataset({ name, projectId, url, datasetId, path, strategy }) {
  return request.post("/datasets/importing", {
    dataset_group_name: name, strategy,
    project_id: projectId,
    input_url: url,
    input_dataset_id: datasetId,
    input_path: path,
  })
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
