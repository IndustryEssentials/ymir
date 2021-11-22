import request from "@/utils/request"

/** keyword service */

/**
 * @param {*} params
 * { q = 0, offset = 0, limit = 10 }
 * @returns
 */
export function getKeywords(params) {
  return request.get("keywords/", { params })
}

/**
 * new and update keywords
 * @param {array} keywords 
 * @returns 
 */
export function updateKeywords(keywords = []) {
  return request.post('/keywords/', {
    keywords,
  })
}
