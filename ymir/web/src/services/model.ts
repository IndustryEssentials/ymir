import request from '@/utils/request'

type ModelId = number

/** model service */
/**
 *
 * @param {number} id
 * @param {number} version
 * @returns
 */
export function getModel(id: ModelId) {
  return request.get(`models/${id}`)
}

/**
 * get model versions by model group id
 * @param {number} group_id
 * @returns
 */
export function getModelVersions(group_id: number) {
  return request.get(`models/`, { params: { group_id, limit: 10000 } })
}

/**
 * @description query models
 * @export
 * @param {YParams.ModelsQuery} { pid, gid, type, state, name, startTime, endTime, orderBy, desc, visible = true, offset = 0, limit = 10 }
 */
export function queryModels({ pid, gid, type, state, name, startTime, endTime, orderBy, desc, visible = true, offset = 0, limit = 10 }: YParams.ModelsQuery) {
  return request.get('models/', {
    params: {
      project_id: pid,
      type,
      state,
      group_id: gid,
      group_name: name,
      visible,
      start_time: startTime,
      end_time: endTime,
      order_by: orderBy,
      is_desc: desc,
      offset,
      limit,
    },
  })
}

/**
 * get models
 * @param {object} param1 {
 *   {number} project_id
 *   {string} name model name
 *   {number} offset  query start
 *   {number} limit query count
 * }
 * @returns
 */
export function getModels(pid: number, { name, offset = 0, limit = 10 }: YParams.GroupsQuery) {
  return request.get('model_groups/', { params: { project_id: pid, name, offset, limit } })
}

/**
 * batch fetch models
 * @param {array} ids
 * @returns
 */
export function batchModels(ids: ModelId[]) {
  return request.get('models/batch', { params: { ids: ids.toString() } })
}

/**
 * delete model version
 * @param {number} id
 * @returns
 */
export function delModel(id: ModelId) {
  return request({
    method: 'delete',
    url: `/models/${id}`,
  })
}

/**
 * delete model group
 * @param {number} id
 * @returns
 */
export function delModelGroup(id: number) {
  return request({
    method: 'delete',
    url: `/model_groups/${id}`,
  })
}

/**
 * @description hide/restore/delete models
 * @export
 * @param {('hide'|'restore'|'delete')} action
 * @param {number} pid
 * @param {ModelId[]} [ids=[]]
 */
export function batchAct(action: 'hide' | 'restore' | 'delete', pid: number, ids: ModelId[] = []) {
  return request.post(`/models/batch`, {
    project_id: pid,
    operations: ids.map((id) => ({ id, action })),
  })
}

/**
 *
 * @param {object} param {
 * {string} projectId
 * {string} name
 * {string} [path] local file path
 * {string} [url]  net url
 * {number} [modelId] copy model id
 * {string} [description]
 * }
 * @returns
 */
export function importModel({ projectId, name, description, url, path, modelId }: YParams.ModelCreateParams) {
  return request.post('/models/importing', {
    project_id: projectId,
    input_model_path: path,
    input_url: url,
    input_model_id: modelId,
    description,
    group_name: name,
  })
}

export function updateModelGroup(id: ModelId, name: string) {
  return request({
    method: 'patch',
    url: `/model_groups/${id}`,
    data: {
      name,
    },
  })
}

/**
 * update model version description
 * @param {number} id
 * @param {string} description
 * @returns
 */
export function updateVersion(id: ModelId, description = '') {
  return request({
    method: 'patch',
    url: `/models/${id}`,
    data: {
      description,
    },
  })
}

/**
 * @description model verification
 * @export
 * @param {YParams.ModelVerifyParams} { projectId, modelStage, urls, image, config }
 */
export function verify({ projectId, modelStage, urls, image, config }: YParams.ModelVerifyParams) {
  const [model, stage] = modelStage
  return request.post(`/inferences/`, {
    project_id: projectId,
    model_id: model,
    model_stage_id: stage,
    image_urls: urls,
    docker_image: image,
    docker_image_config: config,
  })
}

export function setRecommendStage(model: number, stage: number) {
  return request({
    method: 'patch',
    url: `/models/${model}`,
    data: {
      stage_id: stage,
    },
  })
}

/**
 * batch fetch model stages
 * @param {array} ids
 * @returns
 */
export function batchModelStages(ids: ModelId[]) {
  return request.get('model_stages/batch', { params: { ids: ids.toString() } })
}
