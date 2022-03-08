import request from "@/utils/request"

/** project service */
/**
 *
 * @param {array[number]} id
 * @returns
 */
export function getProject(id) {
  return request.get(`projects/${id}`)
}

export function getInterations(id) {
  return request.get(`projects/${id}/interations`)
}

/**
 * @param {*} params
 * { name, offset = 0, limit = 10 }
 * @returns
 */
export function getProjects({ name, offset = 0, limit = 0 }) {
  return request.get("projects/", { params: { name, offset, limit } })
}

/**
 * delete project
 * @param {number} id
 * @returns
 */
export function delProject(id) {
  return request({
    method: "delete",
    url: `/projects/${id}`,
  })
}

/**
 * create a project
 * @param {object} project
 * {
 *   {string}  name
 *   {string}  [description]
 *   {number}  strategy
 *   {number}  [chunk_size]
 *   {number}  type
 *   {number}  [target_iteration]
 *   {number}  [target_map]
 *   {number}  [target_dataset]
 *   {array<string>}  keywords
 * }
 * @returns
 */
export function createProject({
  name,
  description,
  strategy,
  chunk_size,
  type,
  target_iteration,
  target_map,
  target_dataset,
  keywords,
}) {
  return request.post("/projects/", {
    name,
    description,
    mining_strategy: strategy,
    chunk_size,
    training_type: type,
    iteration_target: target_iteration,
    map_target: target_map,
    training_dataset_count_target: target_dataset,
    training_keywords: keywords,
  })
}

/**
 * update project
 * @param {number} id 
 * @param {object} params 
 * {
 * {string}    description
 * {number}    iteration_target
 * {array<string>}    keywords
 * {number}    map_target
 * {string}    name
 * {number}    training_dataset_count_target
 * {number}    type
 * }
 * @returns 
 */
export function updateProject(id, params) {
  return request({
    method: "patch",
    url: `/projects/${id}`,
    data: params,
  })
}
