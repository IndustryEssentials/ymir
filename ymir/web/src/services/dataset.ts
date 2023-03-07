import request from '@/utils/request'
import { AxiosResponse } from 'axios'

/** dataset service */
/**
 * get dataset
 * @export
 * @param {number} id dataset id
 * @param {boolean} verbose for more infomation
 */
export function getDataset(id: number, verbose: boolean) {
  return request.get(`datasets/${id}`, { params: { verbose } })
}

/**
 * @description get dataset versions by group id
 * @export
 * @param {number} gid
 */
export function getDatasetByGroup(gid: number) {
  return request.get(`datasets/`, { params: { group_id: gid, limit: 10000 } })
}

/**
 * @description get datasets by query
 * @export
 * @param {YParams.DatasetsQuery} {
 *   pid,
 *   gid,
 *   type,
 *   objectType,
 *   state,
 *   name,
 *   startTime,
 *   endTime,
 *   visible = true,
 *   offset = 0,
 *   limit = 10,
 *   desc = true,
 *   orderBy,
 * }
 */
export function queryDatasets({
  pid,
  gid,
  type,
  excludeType,
  objectType,
  state,
  name,
  startTime,
  endTime,
  visible = true,
  offset = 0,
  limit = 10,
  desc = true,
  orderBy,
}: YParams.DatasetsQuery) {
  return request.get('datasets/', {
    params: {
      project_id: pid,
      group_id: gid,
      source: type,
      exclude_source: excludeType,
      object_type: objectType,
      state,
      group_name: name,
      offset,
      limit,
      is_desc: desc,
      order_by: orderBy,
      visible,
      start_time: startTime,
      end_time: endTime,
    },
  })
}
/**
 * @description get dataset groups
 * @export
 * @param {number} pid
 * @param {YParams.GroupsQuery} { name, offset = 0, limit = 10 }
 */
export function getDatasetGroups(pid: number, { name, offset = 0, limit = 10 }: YParams.GroupsQuery) {
  return request.get('dataset_groups/', {
    params: {
      project_id: pid,
      name,
      offset,
      limit,
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
export function batchDatasets(pid: number, ids: number[] = [], ck: boolean) {
  return request.get('datasets/batch', {
    params: {
      project_id: pid,
      ids: ids.toString(),
      ck,
    },
  })
}

/**
 * @description delete dataset
 * @export
 * @param {number} id
 */
export function delDataset(id: number) {
  return request({
    method: 'delete',
    url: `/datasets/${id}`,
  })
}

/**
 * @description delete dataset group
 * @export
 * @param {number} id
 */
export function delDatasetGroup(id: number) {
  return request({
    method: 'delete',
    url: `/dataset_groups/${id}`,
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
  return request.post(`/datasets/evaluation`, {
    project_id: pid,
    dataset_ids: datasets,
    confidence_threshold: confidence,
    iou_threshold: iou,
    require_average_iou: averageIou,
    main_ck: ck,
    need_pr_curve: curve
  })
}

/**
 * @description get more analysis info from datasets
 * @export
 * @param {number} pid
 * @param {number[]} datasets
 */
export function analysis(pid: number, datasets: number[]) {
  return request.get(`/datasets/batch`, {
    params: {
      project_id: pid,
      ids: datasets.toString(),
      hist: true,
    },
  })
}

/**
 * @description batch task: hide datasets
 * @export
 * @param {string} action
 * @param {number} pid
 * @param {number[]} [ids=[]]
 */
export function batchAct(action: string, pid: number, ids: number[] = []) {
  return request.post(`/datasets/batch`, {
    project_id: pid,
    operations: ids.map((id) => ({ id, action })),
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

/**
 * @description import a dataset
 * @export
 * @param {YParams.DatasetCreateParams} {
 *  name,   group name
 *  pid,    project id
 *  [url],    remote dataset url
 *  [did],    copied dataset id
 *  [path],   server relative path
 *  [strategy]    annotation strategy
 *  [description]
 * }
 */
export function createDataset({ name, pid, url, did, path, strategy = 2, description }: YParams.DatasetCreateParams) {
  return request.post('/datasets/importing', {
    group_name: name,
    strategy,
    project_id: pid,
    input_url: url,
    input_dataset_id: did,
    input_path: path,
    description,
  })
}

/**
 * @description update dataset, only group name now
 * @export
 * @param {number} id
 * @param {string} name
 */
export function updateDataset(id: number, name: string) {
  return request({
    method: 'patch',
    url: `/dataset_groups/${id}`,
    data: {
      name,
    },
  })
}

/**
 * update dataset version description
 * @param {number} id   dataset version id
 * @param {string} description
 * @returns
 */
export function updateVersion(id: number, description = '') {
  return request({
    method: 'patch',
    url: `/datasets/${id}`,
    data: {
      description,
    },
  })
}

export function getInternalDataset() {
  return request.get('/datasets/public')
}

/**
 * @description check train set and validation set duplication
 * @export
 * @param {number} pid
 * @param {number} trainSet
 * @param {number} validationSet
 */
export function checkDuplication(pid: number, trainSet: number, validationSet: number) {
  return request.post('/datasets/check_duplication', {
    project_id: pid,
    dataset_ids: [trainSet, validationSet],
  })
}

/**
 * @description get negative samples info from dataset limit by keywords
 * @export
 * @param {QueryParams} {
 *   pid,
 *   did,
 *   keywords = [],
 * }
 */
export function getNegativeKeywords({ pid, did, keywords = [] }: YParams.DatasetQuery) {
  return request.get(`/datasets/${did}`, {
    params: {
      project_id: pid,
      keywords: keywords.toString(),
    },
  })
}
