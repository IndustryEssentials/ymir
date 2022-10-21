import { useHistory, useParams } from 'umi'

function useSubmitHandle(type = 'dataset') {
  const history = useHistory()
  const { id: pid } = useParams()

  const handle = (result = {}) => {
    const group =(result[`result_${type}`] || {})[`${type}_group_id`]
    let redirect = `/home/project/${pid}/${type}#${group || ''}`
    history.replace(redirect)
  }
  return handle
}

export default useSubmitHandle
