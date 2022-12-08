import { useDispatch } from 'umi'
import { useRequest as useAhRequest } from 'ahooks'
import { useEffect } from 'react'

type OptionsType = {
  loading?: boolean
}

const useRequest = (effect: string, options: OptionsType = {}) => {
  const dispatch = useDispatch()
  const { loading = true } = options
  const setLoading = (loading: Boolean) =>
    dispatch({
      type: 'common/setLoading',
      payload: loading,
    })

  const fetch = (payload: any) =>
    dispatch({
      type: effect,
      payload,
    })
  const defaultOpts = {
    manual: true,
  }
  // { loading, data, error, params, cancel, refresh, refreshAsync, run, runAsync, mutate }
  const request = useAhRequest(fetch, { ...defaultOpts, ...options })

  useEffect(() => {
    setLoading(loading ? true : !request.loading)
  }, [request.loading])

  return request
}

export default useRequest
