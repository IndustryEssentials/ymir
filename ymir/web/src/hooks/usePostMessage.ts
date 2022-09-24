import { useEffect, useState } from "react"

type Data = {
  type: string,
  data: Object,
  [key: string]: any,
}
const usePostMessage = (domain: string = '*', fixWin: Window | null = null): Array<Function | any> => {
  const [recieved, setRecieved] = useState<Object | null>(null)

  useEffect(() => {
    //// send loaded if have parent window
    window.parent !== window && post('loaded', {}, window.parent)
  }, [window.parent])

  useEffect(() => {
    const handle = (ev: MessageEvent<string>) => {
      const { data, origin } = ev
      try {
        if (origin === domain) {
          const recieveData: Data = JSON.parse(data)

          recievedHandle(recieveData)
        }
      } catch (e) {
        console.error('post message parse error')
      }
    }
    window.addEventListener('message', handle)
    return () => window.removeEventListener('message', handle)
  }, [])

  function post(type: string, data = {}, win: Window | null = null) {
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
  
  function recievedHandle(recieveData: Data) {
    setRecieved({
      ...recieveData,
      finish: (data: Object = {}) => {
        post(`${recieveData.type}_finish`, data)
      }
    })
  }

  return [post, recieved]
}

export default usePostMessage
