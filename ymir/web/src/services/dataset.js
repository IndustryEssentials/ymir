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
  type = 'keywords',
  keywords = [],
  cm = [],
  annoType = [],
  offset = 0,
  limit = 20,
}) {
  return request.get(`datasets/${id}/assets`, {
    params: {
      [type]: keywords.toString() || undefined,
      cm_types: cm.toString() || undefined,
      annotation_types: annoType.toString() || undefined,
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
 * @param {number} iou           iou threadhold
 * @param {number} everageIou    
 * @param {number} confidence   range: [0, 1]
 * @returns 
 */
export function evaluate({ projectId, datasets, iou, everageIou, confidence, ck }) {
  return request.post(`/datasets/evaluation`, {
    project_id: projectId,
    dataset_ids: datasets,
    confidence_threshold: confidence,
    iou_threshold: iou,
    require_average_iou: everageIou,
    ck,
  })
}

/**
 * @param {array} datasets  analysis datasets
 * @returns 
 */
export function analysis(projectId, datasets) {
  return request.get(`/datasets/batch`, {
    params: {
      project_id: projectId,
      ids: datasets.toString(),
      verbose: true,
    }
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
export function createDataset({ name, projectId, url, datasetId, path, strategy = 2, description }) {
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

/**
 * check train set and validation set duplication
 * @param {number} projectId 
 * @param {number} trainSet 
 * @param {number} validationSet 
 * @returns 
 */
export function checkDuplication(projectId, trainSet, validationSet) {
  return request.post('/datasets/check_duplication', {
    project_id: projectId,
    dataset_ids: [trainSet, validationSet],
  })
}

export function getNegativeKeywords({
  projectId,
  dataset,
  keywords,
}) {
  return request.get(`/datasets/${dataset}`, {
    params: {
      project_id: projectId,
      keywords: keywords.toString(),
    }
  })
}
