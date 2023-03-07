import { useDispatch } from 'umi'
import { useRequest as useAhRequest } from 'ahooks'
import { useEffect } from 'react'
type OptionsType<TData, TParams extends any[]> = {
  loading?: boolean
  manual?: boolean
  onBefore?: (params: TParams) => void
  onSuccess?: (data: TData, params: TParams) => void
  onError?: (e: Error, params: TParams) => void
  onFinally?: (params: TParams, data?: TData, e?: Error) => void
  defaultParams?: TParams
  refreshDeps?: (string | number)[]
  refreshDepsAction?: () => void
  loadingDelay?: number
  pollingInterval?: number
  pollingWhenHidden?: boolean
  pollingErrorRetryCount?: number
  refreshOnWindowFocus?: boolean
  focusTimespan?: number
  debounceWait?: number
  debounceLeading?: boolean
  debounceTrailing?: boolean
  debounceMaxWait?: number
  throttleWait?: number
  throttleLeading?: boolean
  throttleTrailing?: boolean
  cacheKey?: string
  cacheTime?: number
  staleTime?: number
  retryCount?: number
  retryInterval?: number
  ready?: boolean
}

const useRequest = <TData, TParams extends any[] = [params?: { [key: string]: any }]>(effect: string, options: OptionsType<TData, TParams> = {}) => {
  const dispatch = useDispatch()
  const { loading = true } = options
  const setLoading = (loading: Boolean) =>
    dispatch({
      type: 'common/setLoading',
      payload: loading,
    })

  const fetch = <D, P>(...args: P[]): Promise<D> => {
    const payload = args[0]
    return dispatch({
      type: effect,
      payload,
    })
  }
  const defaultOpts = {
    manual: true,
  }
  // { loading, data, error, params, cancel, refresh, refreshAsync, run, runAsync, mutate }
  const request = useAhRequest<TData, TParams>(fetch, { ...defaultOpts, ...options })

  useEffect(() => {
    setLoading(loading ? true : !request.loading)
  }, [request.loading])

  return request
}

export default useRequest
