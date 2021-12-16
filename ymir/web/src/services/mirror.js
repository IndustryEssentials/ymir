import request from "@/utils/request"

/** mirror service */
/**
 *
 * @param {number} id
 * @returns
 */
export function getMirror(id) {
  return request.get(`mirrors/${id}`)
}

/**
 * @param {*} params
 * { name, type, start_time = 0, end_time = 0, offset = 0, limit = 10, sort_by: 1|2 }
 * @returns
 */
export function getMirrors(params) {
  return request.get("mirrors/", { params })
}

/**
 * delete mirror
 * @param {number} id
 * @returns
 */
export function delMirror(id) {
  return request({
    method: "delete",
    url: `/mirrors/${id}`,
  })
}

/**
 * create a mirror
 * @param {object} mirror
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
export function createMirror(mirror) {
  return request.post("/mirrors/", mirror)
}

export function updateMirror(id, name) {
  return request({
    method: "patch",
    url: `/mirrors/${id}`,
    data: {
      name,
    },
  })
}
