declare namespace YStates {
  type Root = {
    user: UserState
    iteration: IterationState
    dataset: DatasetState
    prediction: PredictionState
    model: ModelState
    image: ImageState
    keywords: LabelState
    project: ProjectState
    socket: SocketState
    asset: AssetState
    loading: {
      effects: {
        [key: string]: boolean
      }
      global: boolean
      models: {
        [key: string]: boolean
      }
    }
    common: CommonState
  }

  type State = {
    [key: string]: any
  }

  interface CommonState extends State {
    loading: boolean
  }

  interface UserState extends State {
    username: string
    email: string
    phone: string
    avatar: string
    hash: string
    id: number
    role: number
    logined: boolean
    neverShow?: string
  }

  interface ProjectState extends State {
    list: List<YModels.Project>
    projects: IdMap<YModels.Project>
    current: YModels.Project
  }

  interface DatasetState extends State {
    datasets: IdMap<List<YModels.Dataset>>
    versions: IdMap<YModels.Dataset[]>
    dataset: IdMap<YModels.Dataset>
    assets: List<YModels.Asset>
    asset: YModels.Asset
    allDatasets: { [pid: number]: YModels.Dataset[] }
    publicDatasets: YModels.Dataset[]
    query: YParams.DatasetsQuery
  }

  interface PredictionState extends State {
    predictions: IdMap<List<YModels.Prediction>>
    prediction: IdMap<YModels.Prediction>
  }

  interface AssetState extends State {
    assets: IdMap<List<YModels.Asset>>
    asset: IdMap<YModels.Asset>
  }

  interface ModelState extends State {
    models: IdMap<List<YModels.Model>>
    versions: IdMap<YModels.Model[]>
    model: IdMap<YModels.Model>
    allModels: YModels.Model[]
    query: YParams.ModelsQuery
  }

  interface IterationState extends State {
    iterations: List<YModels.Iteration>
    iteration: IdMap<YModels.Iteration>
    actionPanelExpand: boolean
  }

  interface ImageState extends State {
    images: List<YModels.Image>
    image: IdMap<YModels.Image>
  }

  type LabelState = {
    keywords: List<YModels.Keywords>
    keyword: IdMap<YModels.Keywords>
  }

  interface SocketState extends State {
    tasks: YModels.ProgressTask[]
  }
  type EffectSelector = <T extends (state: YStates.Root) => any>(func: T) => Promise<ReturnType<T>>
  type EffectAction = <P = unknown, R = unknown>(action: ActionType<P>) => Promise<R>
  type EffectActionsType = {
    call: <R>(func: Function, ...params: any[]) => Promise<R>
    put: EffectAction & {
      resolve: EffectAction
    }
    select: EffectSelector
    dispatch: EffectAction
  }
  type PayloadType<P extends any = any> = {
    payload: P
  }
  type ActionType<P extends any = any> = {
    type: string
    payload?: P
  }
  type EffectType<P extends any = any, R extends any = any> = (action: PayloadType<P>, dispatch: EffectActionsType) => R
  type ReducerType<S> = (state: S, action: ActionType) => S
  type EffectsType = {
    [key: string]: EffectType
  }
  type ReducersType<S> = {
    [key: string]: ReducerType<S>
  }
  interface Dispatch<A extends ActionType> {
    <T extends A, R = any>(action: T): Promise<R>
  }

  interface History {
    length: number
    listen(listener: (location: Location, action: 'PUSH' | 'POP' | 'REPLACE') => void): () => void
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

  type PredictionReducers = ReducersType<PredictionState>
  type PredictionStore = StoreType<'prediction', PredictionState>
  type AssetStore = StoreType<'asset', AssetState>
  type SocketStore = StoreType<'socket', SocketState>

  type ResultState<T extends YModels.ResultType> = T extends 'dataset' ? DatasetState : ModelState
  type List<T> = { items: T[]; total: number }
  type IdMap<T> = { [key: string | number]: T }
}
