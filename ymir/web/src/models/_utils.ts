import { isPlainObject } from '@/utils/object'
type PropType<TObj, TProp extends keyof TObj> = TObj[TProp]
type ReducerType = {
  name: string,field: string,
}

export const NormalReducer = <S extends YStates.State, K extends keyof S>(field: K) => {
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

export const createReducers = <S extends YStates.State>(list: ReducerType[]) =>
  list.reduce((prev, { name, field }) => ({ ...prev, [name]: NormalReducer<S, typeof field>(field) }), {})