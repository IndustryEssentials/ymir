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
 * @param {boolean} dry_run only check, fake update
 * @returns 
 */
export function updateKeywords({ keywords = [], dry_run = false }) {
  return request.post('/keywords/', {
    keywords,
    dry_run,
  })
}

/**
 * update keyword
 * @param {string} name
 * @param {array} [aliases] 
 * @returns 
 */
export function updateKeyword({ name, aliases = [] }) {
  return request({
    method: 'PATCH',
    url: `/keywords/${name}`,
    data: {
      aliases,
    }
  })
}

/**
 * get recommend keywords of dataset or global
 * @param {object} param0 
 * {
 *   {array[number]} datasets_ids
 *   {number} limit
 *   {boolean} global default: false
 * }
 * @returns {Promise}
 */
export function getRecommendKeywords({ dataset_ids = [], limit, global = false }) {
  if (!global) {
    return request.get(`/stats/keywords/recommend`, { params: { dataset_ids: dataset_ids.toString(), limit }})
  } else {
    return request.get('/stats/keywords/hot', { params: { limit }})
  }
}
