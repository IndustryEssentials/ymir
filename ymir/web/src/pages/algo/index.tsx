import { getDeploayUrl } from '@/constants/common'
import usePostMessage from '@/hooks/usePostMessage'
import { message } from 'antd'
import { useEffect, useRef, useState } from 'react'
import { getLocale, history, useLocation, useParams, useSelector } from 'umi'
type Params = { [key: string]: any }

const base = getDeploayUrl()

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
  const { module = 'public' } = useParams<Params>()
  const location: Params = useLocation()
  const iframe: { current: HTMLIFrameElement | null } = useRef(null)
  const [url, setUrl] = useState(base)
  const [post, recieved] = usePostMessage(base)
  const [key, setKey] = useState(Math.random())

  useEffect(() => {
    if (!location.state?.reload) {
      const r = Math.random()
      setKey(r)
      const self = window.location.origin
      const lang = getLocale()
      const url = `${base}${pages[module].path}?from=${self}&userId=${userId}&userName=${userName || ''}&lang=${lang}&r=${r}`
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
        const mod = page === 'public' ? '' : `/${page}`
        history.push(`/home/algo${mod}`, { reload: true })
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
    <iframe key={key} ref={iframe} src={url} style={iframeStyles}></iframe>
  </div>
}

export default Algo
