import { useEffect, useRef, useState } from 'react'
import { getLocale, useHistory, useLocation, useParams, useRouteMatch } from 'umi'
import { message } from 'antd'
import { useSelector } from 'react-redux'

import { getPublicImageUrl } from '@/constants/common'
import usePostMessage from '@/hooks/usePostMessage'
import useRequest from '@/hooks/useRequest'
import { ROLES } from '@/constants/user'
import t from '@/utils/t'

type UserType = {
  username: string
  id: number
  uuid: string
  role: number
}
type Params = { [key: string]: any }
type DataType = {
  path?: string
  name?: string
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
  imageAdd: { url: '/home/image/add', privilege: [ROLES.SUPER, ROLES.ADMIN] },
}
const pages: Params = {
  portal: { path: '/img', action: 'pageInit' },
  publish: { path: '/img/publish', action: 'pageInit' },
}

const defaultPage = 'portal'

const PublicImage = () => {
  const history = useHistory()
  const { url: currentPage } = useRouteMatch()
  if (!base) {
    return <div>Image Community is not READY</div>
  }
  const { username: userName, id: userId, uuid, role } = useSelector<{ user: UserType }, UserType>(({ user }) => user)
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
      const query = location.search || '?'

      const url = `${base}${pages[module].path}${query}from=${self}&userId=${userId}&uuid=${uuid}&userName=${userName || ''}&lang=${lang}&r=${r}`
      setUrl(url)
    }
    history.replace({ state: {} })
  }, [module])

  useEffect(() => {
    console.log('recieved changed:', recieved)
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
        const name = recieved.data?.name || ''
        const params = recieved.data?.params || {}
        const page = internalPages[name] || {}
        if (!page.url) {
          return
        }
        if (!page.privilege?.includes(role)) {
          return message.error(t('error110205'))
        }
        history.push(page.url, {
          record: {
            name: params.name,
            docker_name: params.image_addr,
            description: params.description,
          },
        })
        send('toPageSuccess', { name })
      },
      async checkImage() {
        const url = recieved.data?.url
        if (url) {
          const result = await checkImageExist({ url })
          send('imageChecked', {
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
  function send(type: string, params: Params) {
    if (iframe.current?.contentWindow) {
      post(type, params, iframe.current.contentWindow)
    }
  }
  return (
    <div style={{ margin: '0 -20px' }}>
      <iframe key={key} ref={iframe} src={url} style={iframeStyles}></iframe>
    </div>
  )
}

export default PublicImage
