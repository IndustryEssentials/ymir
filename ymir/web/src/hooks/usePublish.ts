import { ModelVersion } from '@/interface/model'
import { useEffect, useState } from 'react'
import { getLocale, useSelector } from 'umi'
import usePostMessage from './usePostMessage'

const base = 'http://192.168.28.58:8000'
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
  const [post, recieved] = usePostMessage(base)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const { id: userId, username: userName } = useSelector((state: { user: any }) => state.user)

  useEffect(() => {
    // finish publish
    console.log('recieved:', recieved)
    if (recieved?.type === 'loaded') {

    }
  }, [recieved])

  const publish = (data: ModelVersion, callback = () => { }) => {
    if (loading) {
      return
    }
    setLoading(true)
    const lang = getLocale()
    const url = window.location.origin + data.url
    const stage = data.stages?.find(stg => stg.id === data.recommendStage)?.name
    const params = {
      lang, userId, userName,
      modelId: data.id,
      modelName: data.name,
      stage,
      url,
    }
    // create iframe
    console.log('publish params:', params)
    createIframe(params)
  }

  return [publish, result]
}

export default usePublish
