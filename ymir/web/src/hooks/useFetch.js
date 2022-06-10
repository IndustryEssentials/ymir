import { useState } from 'react'
import { useDispatch } from 'umi'

const useFetch = (effect) => {
  const dispatch = useDispatch()
  const fetch = payload => dispatch({
    type: effect,
    payload,
  })
  const [result, setResult] = useState(null)

  const getResult = async ({...payload}) => {
    const result = await fetch(payload)
    if (result) {
      setResult(result)
    }
  }

  return [result, getResult]
}

export default useFetch
