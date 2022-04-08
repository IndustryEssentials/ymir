import axios from "axios"
import storage from "@/utils/storage"
import t from "@/utils/t"
import { history } from "umi"
import { getDvaApp } from 'umi'
import { message } from "antd"

const getBaseURL = () => {
  const envUrl = process.env.APIURL
  if (process.env.NODE_ENV === 'development') {
    return envUrl
  }
  return window.baseConfig?.APIURL || envUrl
}

// console.log('base url: ', getBaseURL(), process.env)

const request = axios.create({
  baseURL: getBaseURL(),
  // timeout: 1,
})

request.interceptors.request.use(
  (config) => {
    config.headers["Content-Type"] =
      config.headers["Content-Type"] || "application/json"
    config.headers["Authorization"] = `Bearer ${storage.get("access_token")}`
    return config
  },
  (err) => {
    console.error(err)
    return err
  }
)

request.interceptors.response.use(
  (res) => {
    if (res.data.code !== 0) {
      message.error(t(`error${res.data.code}`))
      if (res.data.code === 110104) {
        return logout()
      }
    }

    return res.data
  },
  (err) => {
    let authrized = [401, 403]
    if (authrized.includes(err.request.status)) {
      return logout()
    } else if (err.request.status === 504) {
      message.error(t('error.timeout'))
    } else {
      const res = err.response
      if (res && res.data && res.data.code) {
        if (res.data.code === 110104) {
          return logout()
        }
        return message.error(t(`error${res.data.code}`))
      }
    }

    console.error(err.request.statusText)
    throw new Error(err)
  }
)

function logout() {
  getDvaApp()._store.dispatch({
    type: 'user/loginout'
  })
}

export default request
