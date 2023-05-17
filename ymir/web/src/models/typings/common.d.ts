import { History } from 'umi'
import Stores from '../'

type State = {
  [key: string]: any
}
type Action<P extends any = any> = {
  type: string
  payload?: P
}
interface Dispatch<A extends Action> {
  <T extends A, R = any>(action: T): Promise<R>
}
type EffectSelector = <R extends (state: Stores) => any>(selector: R) => ReturnType<R>
type EffectAction = <P = unknown, R = unknown>(action: Action<P>) => Promise<R>
type EffectActionsType = {
  call: <R>(func: Function, ...params: any[]) => Promise<R>
  put: EffectAction & {
    resolve: EffectAction
  }
  dispatch: EffectAction
  select: EffectSelector
}
type Effect<P = any, R = any> = (action: { payload: P }, dispatch: EffectActionsType) => R
type Reducer<S> = (state: S, action: Action) => S

type EffectsType = {
  [key: string]: Effect
}
type ReducersType<S> = {
  [key: string]: Reducer<S>
}

type Subscription = (
  actions: {
    history: History
    dispatch: Dispatch<any>
  },
  done: Function,
) => void | Function

type StoreType<name extends string, S extends { [key: string]: any }> = {
  namespace: name
  state: S
  reducers: ReducersType<S>
  effects?: EffectsType
  subscriptions?: {
    [key: string]: Subscription
  }
}

type List<T> = { items: T[]; total: number }
type IdMap<T> = { [key: string | number]: T }

export { StoreType, List, IdMap, Reducer, ReducersType, Effect, EffectsType, State }
