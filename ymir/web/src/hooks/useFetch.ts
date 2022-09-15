import { useEffect, useState } from 'react'
import { useDispatch } from 'umi'

const useFetch = (effect: string, initResult: any = null, loading: Boolean = true) => {
  const dispatch = useDispatch()
  const setLoading = (loading: Boolean) => dispatch({
    type: 'common/setLoading',
    payload: loading
  })
  useEffect(() => setLoading(loading), [loading])

  const fetch = (payload: any) => dispatch({
    type: effect,
    payload,
  })
  const [result, setResult] = useState(initResult)

  const getResult = async (payload: any) => {
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
