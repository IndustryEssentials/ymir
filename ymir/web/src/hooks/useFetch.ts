import { useState } from 'react'
import { useDispatch } from 'umi'

const useFetch = (effect: string, initResult: any = null) => {
  const dispatch = useDispatch()
  const fetch = (payload: any) => dispatch({
    type: effect,
    payload,
  })
  const [result, setResult] = useState(initResult)

  const getResult = async (payload: any) => {
    const result = await fetch(payload)
    if (typeof result !== 'undefined') {
      setResult(result)
    }
    return result
  }

  return [result, getResult, setResult]
}

export default useFetch
