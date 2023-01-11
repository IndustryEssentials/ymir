import { useEffect, useState } from 'react'
import { useHistory } from 'umi'

type DefaultDataType = {
  type: string
  data: {
    path?: string
  }
  finish?: (data: { [key: string]: any }) => void
}
type Data<D> = D extends DefaultDataType ? D : DefaultDataType

const usePostMessage = <RecievedType extends DefaultDataType>(domain: string = '*', fixWin: Window | null = null): [Function, RecievedType | undefined] => {
  // type RecievedType = Data<DataType>
  const [recieved, setRecieved] = useState<RecievedType>()
  const history = useHistory()

  useEffect(() => {
    //// send loaded if have parent window
    window.parent !== window && post('loaded', {}, window.parent)
  }, [window.parent])

  useEffect(() => {
    const handle = (ev: MessageEvent<string>) => {
      const { data, origin } = ev
      try {
        if (origin === domain) {
          const recieveData: RecievedType = JSON.parse(data)

          if (recieveData.type === 'redirect' && recieveData?.data?.path) {
            history.push(recieveData.data.path)
          } else {
            recievedHandle(recieveData)
          }
        }
      } catch (e) {
        console.error('post message parse error')
      }
    }
    window.addEventListener('message', handle)
    return () => window.removeEventListener('message', handle)
  }, [])

  function post(type: string, data: { [key: string]: any } = {}, win?: Window) {
    const target = win || fixWin
    if (!target) {
      return console.error('target window is required')
    }
    const message = JSON.stringify({
      type,
      data,
    })
    target.postMessage(message, domain)
  }

  function recievedHandle(recieveData: RecievedType) {
    const data: RecievedType = {
      ...recieveData,
      finish: (data) => {
        post(`${recieveData.type}_finish`, data)
      },
    }
    setRecieved(data)
  }

  return [post, recieved]
}

export default usePostMessage
