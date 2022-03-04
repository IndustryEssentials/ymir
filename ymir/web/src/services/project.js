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
export function createProject(project) {
  return request.post("/projects/", project)
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
