import { useHistory } from 'umi'

function useSubmitHandle(type = 'dataset') {
  const history = useHistory()

  const handle = (result = {}) => {
    const group = type === 'dataset' ?
      result?.result_dataset?.dataset_group_id : result?.result_model?.result_group_id
    let redirect = `/home/project/${pid}/dataset#${group || ''}`
    history.replace(redirect)
  }
  return handle
}

export default useSubmitHandle
