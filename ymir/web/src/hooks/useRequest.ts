import { useDispatch } from 'umi'
import { useRequest as useAhRequest } from 'ahooks'

const useRequest = (effect: string, options = {}) => {
  const dispatch = useDispatch()

  const fetch = (payload: any) =>
    dispatch({
      type: effect,
      payload,
    })
  const defaultOpts = {
    manual: true,
  }
  // { loading, data, error, params, cancel, refresh, refreshAsync, run, runAsync, mutate }
  return useAhRequest(fetch, { ...defaultOpts, ...options })
}

export default useRequest
