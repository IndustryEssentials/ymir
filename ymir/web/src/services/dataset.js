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
  return request.get(`datasets/`, { params: { group_id, limit: 10000 } })
}

/**
 * get datasets
 * @param {object} param1 {
 *   {number}   project_id
 *   {number}   [group_id]
 *   {number}   [type]        task type
 *   {number}   [state]       dataset state
 *   {string}   [name]        dataset name
 *   {number}   [offset]      query start
 *   {number}   [limit]       query count 
 *   {boolean}  [visible]     default as true
 *   {boolean}  [is_desc]     default as true
 *   {string}   [order_by]    value as: id, create_datetime, asset_count, source. default as id
 * }
 * @returns 
 */
export function queryDatasets({
  project_id,
  group_id,
  type,
  state,
  name,
  visible = true,
  offset = 0,
  limit = 10,
  is_desc = true,
  order_by
}) {
  return request.get("datasets/", {
    params: { project_id, group_id, type, state, name, offset, limit, is_desc, order_by, visible }
  })
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
  return request({
    method: "delete",
    url: `/dataset_groups/${id}`,
  })
}

/**
 * evalute between gt and target dataset
 * @param {number} projectId    project id
 * @param {number} datasets      evaluational datasets
 * @param {number} gt           ground truth dataset
 * @param {number} confidence   range: [0, 1]
 * @returns 
 */
export function evaluate({ projectId, datasets, gt, confidence }) {
  return request.post(`/datasets/evaluation`, {
    project_id: projectId,
    other_dataset_ids: datasets,
    gt_dataset_id: gt,
    confidence_threshold: confidence,
  })
}

/**
 * hide datasets
 * @param {number} projectId
 * @param {number} ids
 * @returns
 */
export function batchAct(action, projectId, ids = []) {
  return request.post(`/datasets/batch`, {
    project_id: projectId,
    operations: ids.map(id => ({ id, action, }))
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
 *   {string} [description]
 * }
 * @returns
 */
export function createDataset({ name, projectId, url, datasetId, path, strategy, description }) {
  return request.post("/datasets/importing", {
    group_name: name, strategy,
    project_id: projectId,
    input_url: url,
    input_dataset_id: datasetId,
    input_path: path,
    description,
  })
}

export function updateDataset(id, name) {
  return request({
    method: "patch",
    url: `/dataset_groups/${id}`,
    data: {
      name,
    },
  })
}

export function getInternalDataset() {
  return request.get('/datasets/public')
}
