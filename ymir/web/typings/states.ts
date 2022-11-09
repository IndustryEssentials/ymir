declare namespace YStates {
  type Root = {
    user: UserState
    iteration: IterationState
    dataset: DatasetState
    model: ModelState
    image: ImageState
    keywords: LabelState
    project: ProjectState
  }

  type UserState = {
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

  type ProjectState = {
    list: List<YModels.Project>
    projects: IdMap<YModels.Project>
    current: YModels.Project
  }

  type DatasetState = {
    datasets: List<YModels.Dataset>
    versions: IdMap<YModels.Dataset[]>
    dataset: IdMap<YModels.Dataset>
    assets: List<YModels.Asset>
    asset: YModels.Asset
    allDatasets: YModels.Dataset[]
    publicDatasets: YModels.Dataset[]
  }

  type ModelState = {
    models: List<YModels.Model>
    versions: IdMap<YModels.Model[]>
    model: IdMap<YModels.Model>
    allModels: YModels.Model
  }

  type IterationState = {
    iterations: List<YModels.Iteration>
    iteration: IdMap<YModels.Iteration>
    actionPanelExpand: boolean
  }

  type ImageState = {
    images: List<YModels.Image>
    image: YModels.Image
  }

  type LabelState = {
    keywords: List<YModels.Keywords>
    keyword: IdMap<YModels.Keywords>
  }

  type ResultState<T extends YModels.ResultType> = T extends 'dataset' ? DatasetState : ModelState
  type List<T> = { items: T[]; total: number }
  type IdMap<T> = { [key: string | number]: T }
}
