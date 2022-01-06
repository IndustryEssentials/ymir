import request from '@/utils/request'

const getBaseURL = () => {
  const envUrl = process.env.APIURL
  if (process.env.NODE_ENV === 'development') {
    return envUrl
  }
  return window.baseConfig?.APIURL || envUrl
}
export function getUploadUrl() {
  return getBaseURL() + 'uploadfile/'
}

export function getHistory({ type, id, max_hops }) {
  return request.get('/graphs/', { params: { type, id, max_hops } })
}

export function getTensorboardLink(hash) {
  return `/tensorboard/#scalars&regexInput=${hash}`
}

/**
 * get stats of dataset, model and task
 * @param {
 * q {string} dataset|model|task
 * limit {number} number of items fetch by dataset and model
 * type {number} day|week|month
 * } 
 * @returns 
 */
export function getStats({ q, limit = 8, type='day' }) {
  const params = { q, limit, precision: type }
  return request.get('/stats/', { params })
}

/**
 * get runtime config of backend
 * @param {object} param0 
 * {
 *   name {string}
 *   hash {string}
 *   type {number} 1(training)|2(mining) config type
 * }
 * @returns 
 */
export function getRuntimes ({ name, hash, type }) {
  return request.get('/runtimes/', { params: { name, hash, type }})
}

export function getSysInfo() {
  return request.get('/sys_info/')
}
