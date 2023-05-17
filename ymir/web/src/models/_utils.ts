import { Backend } from '@/constants'
import { isPlainObject } from '@/utils/object'
import { capitalize } from '@/utils/string'
import Root from '.'
import { Effect, List } from './typings/common.d'
export type ReducerType<S> = {
  name: string
  field: keyof S
}
type Reducer<S, K extends keyof S> = (state: S, { payload }: { payload?: S[K] }) => S
type ReducerProducer = <S, K extends keyof S>(field: K) => Reducer<S, K>

const NormalReducer: ReducerProducer = (field) => {
  return (state, { payload }) => {
    const current = state[field]
    const update = payload && isPlainObject(current) ? { ...current, ...payload } : payload
    return {
      ...state,
      [field]: update,
    }
  }
}

const createReducers = <S>(list: ReducerType<S>[]) => list.reduce((prev, { name, field }) => ({ ...prev, [name]: NormalReducer<S, typeof field>(field) }), {})

const createReducersByState = <S extends Root[keyof Root]>(state: S) => {
  const fields = Object.keys(state) as (keyof S)[]
  return fields.reduce<{ [key: string]: Reducer<S, keyof S> }>((prev, field) => {
    const name = `Update${capitalize(field as string)}`
    return { ...prev, [name]: NormalReducer<S, keyof S>(field) }
  }, {})
}

const transferList = <R extends any = any>(listResponse: List<Backend>, func: (data: Backend) => R) => {
  const { items, total } = listResponse
  return { items: items.map((item) => func(item)), total }
}

const createEffect = <PT = any, R = unknown>(func: Effect<PT, R>) => func

export { NormalReducer, createReducers, createReducersByState, transferList, createEffect }
