import { isPlainObject } from '@/utils/object'
type PropType<TObj, TProp extends keyof TObj> = TObj[TProp]
export type ReducerType = {
  name: string
  field: string
}

const NormalReducer = <S extends YStates.State, K extends keyof S>(field: K) => {
  type FieldType = PropType<S, K>

  return (state: S, { payload }: { payload: FieldType }): S => {
    const current = state[field]
    const update = isPlainObject(current) ? { ...current, ...payload } : payload
    return {
      ...state,
      [field]: update,
    }
  }
}

const createReducers = <S extends YStates.State>(list: ReducerType[]) =>
  list.reduce((prev, { name, field }) => ({ ...prev, [name]: NormalReducer<S, typeof field>(field) }), {})

const transferList = <R>(listResponse: YModels.ResponseResultList, func: (data: YModels.BackendData) => R): YStates.List<R> => {
  const { items, total } = listResponse
  return { items: items.map((item) => func(item)), total }
}

const createEffect = <PT, R = unknown>(func: YStates.EffectType<PT, R>) => func

export { NormalReducer, createReducers, transferList, createEffect }
