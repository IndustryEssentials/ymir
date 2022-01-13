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
 * q {string} mms|hms|hkw|ds|ts
 * limit {number} number of items fetch by dataset and model
 * type {number} day|week|month
 * } 
 * @returns 
 */
export function getStats({ q, limit = 8, type='day' }) {
  const maps = {
    'mms': { path: 'models/map', },
    'hms': { path: 'models/hot', },
    'hkw': { path: 'keywords/hot', },
    'ds': { path: 'datasets/hot', },
    'ts': { path: 'tasks/count', query: { precision: type } }
  }
  return request.get(`/stats/${maps[q].path}`, { limit, ...(maps[q].query || {}) })
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
