import { isPlainObject } from '@/utils/object'

export const NormalReducer =
  (field: string) =>
  (state: YStates.State, { payload }: { payload: any }) => {
    const current = state[field]
    const update = isPlainObject(current) ? { ...current, ...payload } : payload
    return {
      ...state,
      [field]: update,
    }
  }
