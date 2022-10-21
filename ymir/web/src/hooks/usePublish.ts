import { message } from 'antd'
import { useEffect, useState } from 'react'
import { getLocale, useSelector } from 'umi'

import { getDeployUrl } from '@/constants/common'
import { ModelVersion } from '@/interface/model'
import t from '@/utils/t'

const base = getDeployUrl()
const id = 'publishIframe'

const createIframe = (params = {}) => {
  const url = `${base}/postModelMsg?data=${encodeURIComponent(JSON.stringify(params))}`
  let iframe = document.createElement('iframe')
  document.body.appendChild(iframe)
  iframe.id = id
  iframe.style.position = 'absolute'
  iframe.style.top = '-1000px'
  iframe.style.left = '-1000px'
  iframe.src = url
  return iframe
}

const usePublish = () => {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const { id: userId, username: userName } = useSelector((state: { user: any }) => state.user)

  const publish = (data: ModelVersion) => {
    const key = 'publish'
    if (loading) {
      return
    }
    setLoading(true)
    message.loading({ content: t('algo.publish.tip.loading'), key })

    const lang = getLocale()
    const url = window.location.origin + data.url
    const stage = data.stages?.find(stg => stg.id === data.recommendStage)?.name
    const params = {
      lang, userId, userName,
      modelId: data.id,
      modelName: `${data.name} ${data.versionName}`,
      stage,
      url,
    }
    // create iframe
    console.log('publish params:', params)
    createIframe(params)
    setTimeout(() => {
      setLoading(false)
      message.success({ content: t('algo.publish.tip.success'), key })
    }, 2000)
  }

  return [publish, result]
}

export default usePublish
