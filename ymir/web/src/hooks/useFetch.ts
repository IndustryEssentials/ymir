import { useState } from 'react'
import { useDispatch } from 'umi'

const useFetch = (effect: string, initResult: any = null, hideLoading: Boolean = false) => {
  const dispatch = useDispatch()
  const setLoading = (loading: Boolean) => dispatch({
    type: 'common/setLoading',
    payload: loading
  })

  const fetch = (payload: any) => dispatch({
    type: effect,
    payload,
  })
  const [result, setResult] = useState(initResult)

  const getResult = async (payload: any) => {
    setLoading(!hideLoading)
    const result = await fetch(payload)
    setLoading(true)
    if (typeof result !== 'undefined') {
      setResult(result)
    }
    return result
  }

  return [result, getResult, setResult]
}

export default useFetch
