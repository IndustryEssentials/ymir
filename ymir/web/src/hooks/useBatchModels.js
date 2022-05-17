import { useState } from 'react'
import { useDispatch } from 'umi'

const useBatchModels = () => {
  const dispatch = useDispatch()
  const batch = ids => dispatch({
    type: 'model/batchModels',
    payload: ids
  })
  const [models, setModels] = useState([])

  const getModels = async (ids = []) => {
    if (!ids.length) {
      return
    }
    const result = await batch(ids)
    if (result) {
      setModels(result)
    }
  }

  return [models, getModels]
}

export default useBatchModels
