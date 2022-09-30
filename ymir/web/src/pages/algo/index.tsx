import { DEPLOY_MODULE_URL } from '@/constants/common'
import usePostMessage from '@/hooks/usePostMessage'
import { message } from 'antd'
import { useEffect, useRef, useState } from 'react'
import { getLocale, history, useLocation, useParams, useSelector } from 'umi'
type Params = { [key: string]: any }

const base = DEPLOY_MODULE_URL || ''

const pages: Params = {
  public: { path: '/publicAlgorithm', action: 'pageInit' },
  mine: { path: '/algorithmManagement', action: 'pageInit' },
  device: { path: '/device', action: 'pageInit' },
  support: { path: '/supportDeviceList', action: 'pageInit' },
}

const Algo = () => {
  if (!base) {
    return <div>Algorithm Store is not READY</div>
  }
  const { username: userName, id: userId } = useSelector((state: Params) => state.user)
  const { module } = useParams<Params>()
  const location: Params = useLocation()
  const iframe: { current: HTMLIFrameElement | null } = useRef(null)
  const [url, setUrl] = useState(base)
  const [post, recieved] = usePostMessage(base)

  useEffect(() => {
    if (!location.state?.reload) {
      const self = window.location.origin
      const lang = getLocale()
      const url = `${base}${pages[module].path}?from=${self}&userId=${userId}&userName=${userName || ''}&lang=${lang}&r=${Math.random()}`
      setUrl(url)
    }
    history.replace({ state: {} })
  }, [module])

  useEffect(() => {
    if (!recieved) {
      return
    }
    if (recieved.type === 'loaded') {
      // send()
    } else if (recieved.type === 'pageChanged') {
      const page = Object.keys(pages).find(key => (recieved.data?.path || '').includes(pages[key].path))
      if (page !== module) {
        history.push(`/home/algo/${page}`, { reload: true })
      }
    }
  }, [recieved])

  function getPageParams(module: string) {
    const lang = getLocale()
    return {
      module,
      userId,
      userName,
      lang,
    }
  }

  function send() {
    if (iframe.current?.contentWindow) {
      const params = getPageParams(module)
      post(pages[module].action, params, iframe.current.contentWindow)
    }
  }

  const iframeStyles = {
    border: 'none',
    width: '100%',
    height: 'calc(100vh - 120px)',
  }
  return <div style={{ margin: '0 -20px' }}>
    <iframe ref={iframe} src={url} style={iframeStyles}></iframe>
  </div>
}

export default Algo
