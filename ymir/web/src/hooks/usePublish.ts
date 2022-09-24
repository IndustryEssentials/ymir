import { useEffect } from 'react'
import usePostMessage from './usePostMessage'

const createIframe = () => {
  const iframe = document.createElement('iframe')
  return iframe
}

const usePublish = () => {
  const [post, recieved] = usePostMessage()

  useEffect(() => {
    // finish publish
  console.log('recieved:', recieved)
  }, [recieved])

  const callback = () => {

  }
  const publish = (data: Object, callback = () => {}) => {
    // todo
    // create iframe
    const iframe = createIframe()

    // // send message
    post('publish', data, iframe.contentWindow)
  }

  return publish
}

export default usePublish
