import axios from 'axios'
import storage from '@/utils/storage'
import t from '@/utils/t'
import { getDvaApp } from 'umi'
import { message } from 'antd'

const getBaseURL = () => {
  const envUrl = process.env.APIURL
  if (process.env.NODE_ENV === 'development') {
    return envUrl
  }
  return window.baseConfig?.APIURL || envUrl
}

const request = axios.create({
  baseURL: getBaseURL(),
  // timeout: 1,
})

request.interceptors.request.use(
  (config) => {
    const headers = config.headers || {}
    headers['Content-Type'] = headers['Content-Type'] || 'application/json'
    headers['Authorization'] = `Bearer ${storage.get('access_token')}`
    config.headers = headers
    return config
  },
  (err) => {
    console.error(err)
    return err
  },
)

request.interceptors.response.use(
  (res) => {
    if (res.data.code !== 0) {
      message.error(t(`error${res.data.code}`))
      if ([110104, 110112].includes(res.data.code)) {
        logout()
      }
    }

    return res.data
  },
  (err) => {
    let authrized = [401, 403]
    let serviceErrorCode = [500, 504, 502]
    if (authrized.includes(err.request.status)) {
      return logout()
    } else if (serviceErrorCode.includes(err.request.status)) {
      message.error(t(`error.${err.request.status}`))
    } else {
      const res = err.response
      if (res?.data?.code) {
        if (res.data.code === 110104) {
          return logout()
        }
        message.error(t(`error${res.data.code}`))
        return res.data
      }
    }

    return { code: err.request.status }
  },
)

function logout() {
  getDvaApp()._store.dispatch({
    type: 'user/loginout',
  })
}

export default request
