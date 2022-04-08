import request from "@/utils/request"

/** model service */
/**
 *
 * @param {number} id
 * @param {number} version
 * @returns
 */
export function getModel(id) {
  return request.get(`models/${id}`)
}

/**
 * get model versions by model group id
 * @param {number} group_id 
 * @returns 
 */
export function getModelVersions(group_id) {
  return request.get(`models/`, { params: { group_id, is_desc: false, limit: 10000 } })
}

/**
 * query models
 * @param {object} param1 {
 *   {number} project_id 
 *   {number} type task type
 *   {number} state model state
 *   {string} name model name
 *   {number} offset  query start
 *   {number} limit query count 
 * }
 * @returns 
 */
export function queryModels({ project_id, type, state, name, offset = 0, limit = 10 }) {
  return request.get("models/", { params: { project_id, type, state, name, offset, limit } })
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
export function getModels(project_id, { name, offset = 0, limit = 10 }) {
  return request.get("model_groups/", { params: { project_id, name, offset, limit } })
}

/**
 * batch fetch models
 * @param {array} ids 
 * @returns 
 */
export function batchModels(ids) {
  return request.get('models/batch', { params: { ids: ids.toString() } })
}

/**
 * delete model version
 * @param {number} id
 * @returns
 */
export function delModel(id) {
  return request({
    method: "delete",
    url: `/models/${id}`,
  })
}

/**
 * delete model group
 * @param {number} id
 * @returns
 */
export function delModelGroup(id) {
  return request({
    method: "delete",
    url: `/model_groups/${id}`,
  })
}

/**
 * 
 * @param {object} param {
 * {string} projectId
 * {string} name
 * {string} [url] 
 * {number} [modelId] model id
 * {string} [description]
 * }
 * @returns 
 */
export function importModel({ projectId, name, description, url, modelId, }) {
  return request.post('/models/importing', {
    project_id: projectId,
    input_model_path: url,
    input_model_id: modelId,
    description,
    group_name: name,
  })
}

export function updateModel(id, name) {
  return request({
    method: "patch",
    url: `/model_groups/${id}`,
    data: {
      name,
    },
  })
}

/**
 * model verification
 * @param {number} model_id model id
 * @param {array} image_urls image urls
 * @param {number} image docker image url
 * @returns 
 */
export function verify(model_id, image_urls, image, config) {
  return request.post(`/inferences/`, { model_id, image_urls, docker_image: image, docker_image_config: config })
}
