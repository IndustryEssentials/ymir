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
 * get model versions
 * @param {number} id model id
 * @returns
 */
export function getModelVersions(group_id) {
  return request.get(`models/${group_id}/version`)
}

/**
 * @param {*} params
 * { name, type, start_time = 0, end_time = 0, offset = 0, limit = 10, is_desc = true, order_by: 1|2 }
 * @returns
 */
export function getModels(params) {
  return request.get("models/", { params })
}

/**
 * batch fetch models
 * @param {array} ids 
 * @returns 
 */
export function batchModels(ids) {
  return request.get('models/batch', { params: { ids: ids.toString() }})
}

/**
 * delete model
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
 * create a model
 * @param {object} model
 * {
 *   "hash": "string",
 *   "name": "string",
 *   "map": "string",
 *   "parameters": "string",
 *   "task_id": 0,
 *   "user_id": 0
 * }
 * @returns
 */
export function createModel(model) {
  return request.post("/models/", model)
}

export function updateModel(id, name) {
  return request({
    method: "patch",
    url: `/models/${id}`,
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
export function verify(model_id, image_urls, image) {
  return request.post(`/inferences/`, { model_id, image_urls, docker_image: image })
}
