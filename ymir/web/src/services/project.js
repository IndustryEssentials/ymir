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
 * { name, type, start_time = 0, end_time = 0, offset = 0, limit = 10, is_desc = true, order_by = 1 }
 * @returns
 */
export function getProjects(params) {
  console.log('get projects: ', params)
  return request.get("projects/", { params })
}

export function batchProjects(ids) {
  return request.get('projects/batch', { params: { ids: ids.toString() }})
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
export function createProject(project) {
  return request.post("/projects/", project)
}

export function updateProject(id, name) {
  return request({
    method: "patch",
    url: `/projects/${id}`,
    data: {
      name,
    },
  })
}
