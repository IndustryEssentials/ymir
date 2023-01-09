declare namespace YStates {
  type Root = {
    user: UserState
    iteration: IterationState
    dataset: DatasetState
    model: ModelState
    image: ImageState
    keywords: LabelState
    project: ProjectState
    loading: {
      effects: {
        [key: string]: boolean
      }
    }
  }

  type State = {
    [key: string]: any
  }

  interface UserState extends State {
    username: string
    email: string
    phone: string
    avatar: string
    hash: string
    id: number
    role: number
    logined?: string
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

  type ResultState<T extends YModels.ResultType> = T extends 'dataset' ? DatasetState : ModelState
  type List<T> = { items: T[]; total: number }
  type IdMap<T> = { [key: string | number]: T }
}
