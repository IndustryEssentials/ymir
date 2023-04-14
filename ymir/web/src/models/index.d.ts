import { Message } from '@/constants'
import { Socket } from 'socket.io-client'
import { Loading } from 'umi'
import { IdMap, List, StoreType } from './typings/common.d'

type Root = {
  user: UserState
  iteration: IterationState
  dataset: DatasetState
  prediction: PredictionState
  model: ModelState
  image: ImageState
  keyword: LabelState
  project: ProjectState
  socket: SocketState
  asset: AssetState
  loading: Loading
  common: CommonState
  message: MessageState
}

interface CommonState {
  loading: boolean
}

interface UserState {
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

interface ProjectState {
  list: List<YModels.Project>
  projects: IdMap<YModels.Project>
  current: YModels.Project
}

interface DatasetState {
  datasets: IdMap<List<YModels.Dataset>>
  versions: IdMap<YModels.Dataset[]>
  dataset: IdMap<YModels.Dataset>
  assets: List<YModels.Asset>
  asset: YModels.Asset
  allDatasets: { [pid: number]: YModels.Dataset[] }
  publicDatasets: YModels.Dataset[]
  query: YParams.DatasetsQuery
  total: number
}

interface PredictionState {
  predictions: IdMap<List<YModels.Prediction>>
  prediction: IdMap<YModels.Prediction>
}

interface AssetState {
  assets: IdMap<List<YModels.Asset>>
  asset: IdMap<YModels.Asset>
}

interface ModelState {
  models: IdMap<List<YModels.Model>>
  versions: IdMap<YModels.Model[]>
  model: IdMap<YModels.Model>
  allModels: YModels.Model[]
  query: YParams.ModelsQuery
}

interface MessageState {
  messages: Message[]
  total: number
  fresh: boolean
  latest?: Message
}

interface IterationState {
  iterations: List<YModels.Iteration>
  iteration: IdMap<YModels.Iteration>
  actionPanelExpand: boolean
}

interface ImageState {
  image: IdMap<YModels.Image>
  total: number
}

type LabelState = {
  allKeywords: YModels.Keyword[]
  reload: boolean
}

interface SocketState {
  tasks: YModels.ProgressTask[]
  socket?: Socket
}

type PredictionStore = StoreType<'prediction', PredictionState>
type AssetStore = StoreType<'asset', AssetState>
type SocketStore = StoreType<'socket', SocketState>
type ImageStore = StoreType<'image', ImageState>
type DatasetStore = StoreType<'dataset', DatasetState>
type MessageStore = StoreType<'message', MessageState>

export {
  PredictionStore,
  AssetStore,
  SocketStore,
  ImageStore,
  DatasetStore,
  MessageStore,
  PredictionState,
  AssetState,
  SocketState,
  ImageState,
  DatasetState,
  MessageState,
}

export default Root
