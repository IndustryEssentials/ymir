import { Asset, ClassObject, Dataset, Image, Iteration, Message, Prediction, ProgressTask, Project, Queue, Task, User, UserLogRecord, Model } from '@/constants'
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
  user: User
  logined: boolean
  neverShow?: string
}

interface ProjectState {
  list: List<Project>
  projects: IdMap<Project>
  current: Project
}

interface DatasetState {
  datasets: IdMap<List<Dataset>>
  versions: IdMap<Dataset[]>
  dataset: IdMap<Dataset>
  allDatasets: { [pid: number]: Dataset[] }
  publicDatasets: Dataset[]
  query: YParams.DatasetsQuery
  validDatasetCount: number
  trainingDatasetCount: number
}

interface PredictionState {
  predictions: IdMap<List<Prediction>>
  prediction: IdMap<Prediction>
}

interface AssetState {
  assets: IdMap<List<Asset>>
  asset: IdMap<Asset>
}

interface ModelState {
  models: IdMap<List<Model>>
  versions: IdMap<Model[]>
  model: IdMap<Model>
  allModels: Model[]
  query: YParams.ModelsQuery
}

interface MessageState {
  messages: Message[]
  total: number
  fresh: boolean
  latest?: Message
}

interface IterationState {
  iterations: IdMap<Iteration[]>
  iteration: IdMap<Iteration>
  actionPanelExpand: boolean
}

interface ImageState {
  image: IdMap<Image>
  total: number
  official?: Image
}

type LabelState = {
  allKeywords: ClassObject[]
  reload: boolean
}

interface SocketState {
  tasks: ProgressTask[]
  socket?: Socket
}

type PredictionStore = StoreType<'prediction', PredictionState>
type AssetStore = StoreType<'asset', AssetState>
type SocketStore = StoreType<'socket', SocketState>
type ImageStore = StoreType<'image', ImageState>
type DatasetStore = StoreType<'dataset', DatasetState>
type MessageStore = StoreType<'message', MessageState>
type CommonStore = StoreType<'common', CommonState>
type IterationStore = StoreType<'iteration', IterationState>
type UserStore = StoreType<'user', UserState>

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
  CommonState,
  CommonStore,
  IterationStore,
  IterationState,
  UserState,
  UserStore,
}

export default Root
=======
import { Asset, ClassObject, Dataset, Image, Iteration, Message, Prediction, ProgressTask, Project, Queue, Task, User, UserLogRecord, Model } from '@/constants'
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
  user: User
  logined: boolean
  neverShow?: string
}

interface ProjectState {
  list: List<Project>
  projects: IdMap<Project>
  current: Project
}

interface DatasetState {
  datasets: IdMap<List<Dataset>>
  versions: IdMap<Dataset[]>
  dataset: IdMap<Dataset>
  allDatasets: { [pid: number]: Dataset[] }
  publicDatasets: Dataset[]
  query: YParams.DatasetsQuery
  validDatasetCount: number
  trainingDatasetCount: number
}

interface PredictionState {
  predictions: IdMap<List<Prediction>>
  prediction: IdMap<Prediction>
}

interface AssetState {
  assets: IdMap<List<Asset>>
  asset: IdMap<Asset>
}

interface ModelState {
  models: IdMap<List<Model>>
  versions: IdMap<Model[]>
  model: IdMap<Model>
  allModels: Model[]
  query: YParams.ModelsQuery
}

interface MessageState {
  messages: Message[]
  total: number
  fresh: boolean
  latest?: Message
}

interface IterationState {
  iterations: IdMap<Iteration[]>
  iteration: IdMap<Iteration>
  actionPanelExpand: boolean
}

interface ImageState {
  image: IdMap<Image>
  total: number
  official?: Image
}

type LabelState = {
  allKeywords: ClassObject[]
  reload: boolean
}

interface SocketState {
  tasks: ProgressTask[]
  socket?: Socket
}

type PredictionStore = StoreType<'prediction', PredictionState>
type AssetStore = StoreType<'asset', AssetState>
type SocketStore = StoreType<'socket', SocketState>
type ImageStore = StoreType<'image', ImageState>
type DatasetStore = StoreType<'dataset', DatasetState>
type MessageStore = StoreType<'message', MessageState>
type CommonStore = StoreType<'common', CommonState>
type IterationStore = StoreType<'iteration', IterationState>
type UserStore = StoreType<'user', UserState>

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
  CommonState,
  CommonStore,
  IterationStore,
  IterationState,
  UserState,
  UserStore,
}

export default Root
>>>>>>> e1cbef88 (update typings)
