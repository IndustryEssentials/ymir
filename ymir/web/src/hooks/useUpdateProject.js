import { useState } from 'react'
import { useDispatch } from 'umi'

const useUpdateProject = (id) => {
  const dispatch = useDispatch()
  const updateProject = payload => dispatch({
    type: 'project/updateProject',
    payload,
  })
  const [updated, setUpdated] = useState({})

  const update = async (params = {}) => {
    const result = await updateProject({ id, ...params })
    if (result) {
      setUpdated(result)
    }
  }

  return [updated, update]
}

export default useUpdateProject
