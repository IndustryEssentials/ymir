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
  hash = hash ? hash : ''
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
    'ts': { path: 'tasks/count', query: { precision: type } },
    'ps': { path: 'projects/count', query: { precision: type } }
  }
  return request.get(`/stats/${maps[q].path}`, { params: { limit, ...(maps[q].query || {}) }})
}

export function getSysInfo() {
  return request.get('/sys_info/')
}
