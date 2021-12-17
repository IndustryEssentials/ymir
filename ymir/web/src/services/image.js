import request from "@/utils/request"

/** image service */
/**
 *
 * @param {number} id
 * @returns
 */
export function getImage(id) {
  return request.get(`images/${id}`)
}

/**
 * @param {*} params
 * { name, type, start_time = 0, end_time = 0, offset = 0, limit = 10, sort_by: 1|2 }
 * @returns
 */
export function getImages(params) {
  return request.get("images/", { params })
}

/**
 * delete image
 * @param {number} id
 * @returns
 */
export function delImage(id) {
  return request({
    method: "delete",
    url: `/images/${id}`,
  })
}

/**
 * create a image
 * @param {object} image
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
export function createImage(image) {
  return request.post("/images/", image)
}

export function updateImage(id, name) {
  return request({
    method: "patch",
    url: `/images/${id}`,
    data: {
      name,
    },
  })
}
