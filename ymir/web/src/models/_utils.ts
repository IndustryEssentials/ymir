import { isPlainObject } from '@/utils/object'
import { Effect } from './typings/common.d'
export type ReducerType<S> = {
  name: string
  field: keyof S
}

const NormalReducer = <S, K extends keyof S>(field: K) => {

  return (state: S, { payload }: { payload: S[K] }): S => {
    const current = state[field]
    const update = payload && isPlainObject(current) ? { ...current, ...payload } : payload
    return {
      ...state,
      [field]: update,
    }
  }
}

const createReducers = <S>(list: ReducerType<S>[]) =>
  list.reduce((prev, { name, field }) => ({ ...prev, [name]: NormalReducer<S, typeof field>(field) }), {})

const transferList = <R>(listResponse: YModels.ResponseResultList, func: (data: YModels.BackendData) => R): YStates.List<R> => {
  const { items, total } = listResponse
  return { items: items.map((item) => func(item)), total }
}

const createEffect = <PT = any, R = unknown>(func: Effect<PT, R>) => func

export { NormalReducer, createReducers, transferList, createEffect }
