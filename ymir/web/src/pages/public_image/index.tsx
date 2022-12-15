import { getPublicImageUrl } from '@/constants/common'
import usePostMessage from '@/hooks/usePostMessage'
import useRequest from '@/hooks/useRequest'
import { useEffect, useRef, useState } from 'react'
import { getLocale, useHistory, useLocation, useParams, useRouteMatch } from 'umi'
import { useSelector } from 'react-redux'

type Params = { [key: string]: any }
type DataType = {
  path?: string
  params?: Params
  url?: string
}
type HandlesType = {
  [key: string]: () => void
}
type RecievedType = {
  type: keyof HandlesType extends string ? keyof HandlesType : string
  data: DataType
}

const base = getPublicImageUrl()

const internalPages: Params = {
  imageAdd: '/home/image/add',
}
const pages: Params = {
  portal: { path: '/image', action: 'pageInit' },
}

const defaultPage = 'portal'

const PublicImage = () => {
  const history = useHistory()
  const { url: currentPage } = useRouteMatch()
  if (!base) {
    return <div>Image Community is not READY</div>
  }
  const { username: userName, id: userId } = useSelector(({ user }: { user: { username: string; id: number } }) => user)
  const { module = defaultPage } = useParams<Params>()
  const location = useLocation<Params>()
  const iframe: { current: HTMLIFrameElement | null } = useRef(null)
  const [url, setUrl] = useState(base)
  const [post, recieved] = usePostMessage<RecievedType>(base)
  const [key, setKey] = useState(Math.random())
  const { runAsync: checkImageExist } = useRequest<{ total: number }>('image/getImages')

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
    if (!recieved?.type) {
      return
    }
    recievedHandle(recieved)
  }, [recieved])

  const recievedHandle = (recieved: RecievedType) => {
    const handles: HandlesType = {
      loaded() {},
      pageChanged() {
        const page = Object.keys(pages).find((key) => (recieved.data?.path || '').includes(pages[key].path))
        if (page !== module) {
          const mod = page === defaultPage ? '' : `/${page}`
          history.push(`${currentPage}${mod}`, { reload: true })
        }
      },
      toPage() {
        const name = recieved.data?.path || ''
        const params = recieved.data?.params || {}
        const page = internalPages[name] || ''
        if (!page) {
          return
        }
        history.push(page, params)
      },
      async checkImage() {
        const url = recieved.data?.url
        if (url) {
          const result = await checkImageExist({ url })
          post('imageChecked', {
            url,
            result: result?.total > 0,
          })
        }
      },
    }
    const func = handles[recieved.type]
    return func && func()
  }

  const iframeStyles = {
    border: 'none',
    width: '100%',
    height: 'calc(100vh - 120px)',
  }
  return (
    <div style={{ margin: '0 -20px' }}>
      <iframe key={key} ref={iframe} src={url} style={iframeStyles}></iframe>
    </div>
  )
}

export default PublicImage
