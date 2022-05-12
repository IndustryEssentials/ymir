import { useState } from 'react'
import { useDispatch } from 'umi'

const useProjectStatus = (initPid) => {
  const [pid, setPid] = useState(initPid)
  const dispatch = useDispatch()
  const checkStatus = (pid) => dispatch({ type: 'project/checkStatus', payload: pid, })

  const checkDirty = async () => {
    const result = await checkStatus(pid)
    if (result) {
      return result.is_dirty
    }
  }

  return {
    setPid,
    checkDirty,
  }
}

export default useProjectStatus
