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
    datasets: List<YModels.Dataset>
    versions: IdMap<YModels.Dataset[]>
    dataset: IdMap<YModels.Dataset>
    assets: List<YModels.Asset>
    asset: YModels.Asset
    allDatasets: { [pid: number]: YModels.Dataset[] }
    publicDatasets: YModels.Dataset[]
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
    models: List<YModels.Model>
    versions: IdMap<YModels.Model[]>
    model: IdMap<YModels.Model>
    allModels: YModels.Model
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
  type EffectSelector = <R>(func: (state: YStates.Root) => R) => Promise<R>
  type EffectAction = <P = unknown, R = unknown>(action: ActionType<P>) => Promise<R>
  type EffectActionsType = {
    call: <R>(func: Function, ...params: any[]) => Promise<R>
    put: EffectAction & {
      resolve: EffectAction
    }
    select: EffectSelector
  }
  type ActionType<P extends any = any> = {
    type?: string
    payload: P
  }
  type EffectType<P extends any = any, R extends any = any> = (action: ActionType<P>, dispatch: EffectActionsType) => R
  type ReducerType<S> = (state: S, action: ActionType) => S
  type EffectsType = {
    [key: string]: EffectType
  }
  type ReducersType<S> = {
    [key: string]: ReducerType<S>
  }

  type StoreType<name extends string, S extends { [key: string]: any}> = {
    namespace: name,
    state: S
    effects: EffectsType
    reducers: ReducersType<S>
  }


  type PredictionReducers = ReducersType<PredictionState>
  type PredictionStore = StoreType<'prediction', PredictionState>
  type AssetStore = StoreType<'asset', AssetState>

  type ResultState<T extends YModels.ResultType> = T extends 'dataset' ? DatasetState : ModelState
  type List<T> = { items: T[]; total: number }
  type IdMap<T> = { [key: string | number]: T }
  
}
