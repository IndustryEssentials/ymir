import { ModelVersion } from '@/interface/model'
import { useEffect, useState } from 'react'
import { getLocale, useSelector } from 'umi'
import usePostMessage from './usePostMessage'

const base = 'http://192.168.28.58:8000'
const id = 'publishIframe'

const createIframe = (params = {}) => {
  const url = `/postModelMsg?data=${encodeURIComponent(JSON.stringify(params))}`
  console.log('url:', url)
  let iframe = document.createElement('iframe')
  document.body.appendChild(iframe)
  iframe.id = id
  iframe.style.display = 'none'
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
    console.log('data:', data, lang, userId, userName)
    const url = window.location.origin + data.url
    const params = {
      lang, userId, userName,
      modelId: data.id,
      modelName: data.name,
      stage: data.recommendStage,
      url,
    }
    // create iframe
    createIframe(params)
  }

  return [publish, result]
}

export default usePublish
