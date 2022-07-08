import { useState } from 'react'
import { useDispatch } from 'umi'

const useFetch = (effect, initResult = null) => {
  const dispatch = useDispatch()
  const fetch = payload => dispatch({
    type: effect,
    payload,
  })
  const [result, setResult] = useState(initResult)

  const getResult = async (payload) => {
    const result = await fetch(payload)
    if (typeof result !== 'undefined') {
      setResult(result)
    }
    return result
  }

  return [result, getResult]
}

export default useFetch
