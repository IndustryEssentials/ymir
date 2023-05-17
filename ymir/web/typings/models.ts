declare module 'react-xml-viewer'

declare namespace YModels {
  type Labels = string[]
  type DatasetId = number
  type ModelId = number
  type StageId = number
  type ImageId = number

  type Matable<U> = {
    [Type in keyof U]: {
      type: Type
    } & U[Type]
  }[keyof U]

  export type BackendData = {
    [key: string]: any
  }

  export type ResponseResultList<M extends BackendData = BackendData> = {
    items: M[]
    total: number
  }

  export type Response<M extends BackendData = BackendData> = {
    code: number
    result?: M
  }

  export interface Group {
    id: number
    name: string
    projectId: number
    createTime: string
  }

  export interface Result {
    id: number
    groupId?: number
    projectId: number
    type: ObjectType
    name: string
    versionName: string
    version: number
    keywords: Labels
    isProtected?: Boolean
    state: number
    createTime: string
    updateTime: string
    hash: string
    taskId: number
    progress: number
    taskState: number
    taskType: number
    duration: number
    durationLabel?: string
    taskName: string
    project?: Project
    hidden: boolean
    description: string
    needReload?: boolean
  }

  enum ObjectType {
    ObjectDetection = 2,
    SemanticSegmentation = 3,
    InstanceSegmentation = 4,
  }

  type Keywords = {
    [key: string]: number
  }
  type CK = {
    [key: string]: string | number
  }
  type CKCount = { [key: string]: number }
  type CKItem = { keyword: string; count: number; children?: CKItem[] }
  type CKCounts = {
    keywords: CKItem[]
    counts: CKCount
    subKeywordsTotal: number
    total: CKCount
  }
  type AnnotationsCount = {
    count: Keywords
    keywords: Labels
    negative: number
    total: number
  }
  type AnylysisAnnotation = {
    keywords: Keywords
    total: number
    average: number
    negative: number
    totalArea: number
    quality: Array<BackendData>
    areaRatio: Array<BackendData>
    keywordAnnotaitionCount: Array<BackendData>
    keywordArea: Array<BackendData>
    instanceArea: Array<BackendData>
    crowdedness: Array<BackendData>
    complexity: Array<BackendData>
  }
  export interface DatasetGroup extends Group {
    versions?: Array<Dataset>
  }

  export interface Dataset<P = TaskParams> extends Result {
    groupId: number
    keywordCount: number
    isProtected: Boolean
    assetCount: number
    task: Task<P>
    gt?: AnnotationsCount
    cks?: CKCounts
    tags?: CKCounts
    evaluated?: boolean
  }

  export interface Prediction extends Omit<Dataset<InferenceParams>, 'groupId'> {
    inferModelId: number[]
    inferModel?: Model
    inferDatasetId: number
    inferDataset?: Dataset
    inferConfig: ImageConfig
    rowSpan?: number
    evaluated: boolean
    pred: AnnotationsCount
    inferClass?: Array<string>
    odd?: boolean
  }

  type AllResult = Prediction | Dataset | Model

  export interface DatasetAnalysis extends Omit<Dataset, 'gt' | 'pred'> {
    assetHWRatio: Array<BackendData>
    assetArea: Array<BackendData>
    assetQuality: Array<BackendData>
    gt: AnylysisAnnotation
    pred: AnylysisAnnotation
  }

  export interface Asset {
    id: number
    hash: string
    keywords: Labels
    url: string
    type: ObjectType
    width: number
    height: number
    metadata?: {
      width: number
      height: number
      image_channels?: number
      timestamp: {
        start: string
        duration?: number
      }
    }
    size?: number
    annotations: Annotation[]
    evaluated?: boolean
    cks?: CK
  }

  export interface AnnotationBase {
    id: string | number
    keyword: string
    width: number
    height: number
    color?: string
    score?: number
    gt?: boolean
    cm: number
    tags?: CK
  }

  enum AnnotationType {
    BoundingBox = 0,
    Polygon = 1,
    Mask = 2,
  }

  type AnnotationMaps = {
    [AnnotationType.BoundingBox]: BoundingBox
    [AnnotationType.Polygon]: Polygon
    [AnnotationType.Mask]: Mask
  }

  type Point = {
    x: number
    y: number
  }

  export type Annotation = Matable<AnnotationMaps>

  export type SegAnnotation = Matable<Omit<AnnotationMaps, AnnotationType.BoundingBox>>
  export type DetAnnotation = Matable<Pick<AnnotationMaps, AnnotationType.BoundingBox>>

  export interface BoundingBox extends AnnotationBase {
    type: AnnotationType.BoundingBox
    box: {
      x: number
      y: number
      w: number
      h: number
      rotate_angle?: number
    }
  }

  export interface Polygon extends AnnotationBase {
    type: AnnotationType.Polygon
    polygon: Point[]
  }

  export interface Mask extends AnnotationBase {
    type: AnnotationType.Mask
    mask: string
    decodeMask?: number[][]
    rect?: [x: number, y: number, width: number, height: number]
  }

  export interface Stage {
    id: number
    name: string
    primaryMetric: number
    primaryMetricLabel?: string
    modelId?: number
    modelName?: string
    metrics?: StageMetrics
  }
  export interface ModelGroup extends Group {}
  export interface Model<P = TaskParams> extends Result {
    map: number
    url: string
    task: Task<P>
    stages?: Array<Stage>
    recommendStage: number
  }
  type BaseStageMetrics = {
    primary: number
    tp?: number
    fp?: number
    fn?: number
  }
  interface DetectionStageMetrics extends BaseStageMetrics {
    ap: number
    ar?: number
  }
  interface SemanticStageMetrics extends BaseStageMetrics {
    iou: number
    acc?: number
  }
  interface InstanceStageMetrics extends BaseStageMetrics {
    maskAP: number
    boxAP?: number
  }

  export type StageMetrics = DetectionStageMetrics | SemanticStageMetrics | InstanceStageMetrics

  export interface Project {
    id: number
    name: string
    type: number
    typeLabel: string
    keywords: Labels
    candidateTrainSet: number
    trainSet?: DatasetGroup
    testSet?: Dataset
    miningSet?: Dataset
    testingSets?: Array<number>
    setCount: number
    trainSetVersion?: number
    model?: number
    modelStage?: Array<number>
    miningStrategy: number
    chunkSize?: number
    currentIteration?: Iteration
    round: number
    currentStep: string
    createTime: string
    updateTime: string
    description?: string
    isExample?: boolean
    hiddenDatasets: Array<number>
    hiddenModels: Array<number>
    enableIteration: boolean
    totalAssetCount: number
    datasetCount: number
    datasetProcessingCount: number
    datasetErrorCount: number
    modelCount: number
    modelProcessingCount: number
    modelErrorCount: number
  }

  export type ImageConfig = { [key: string]: number | string }
  export type DockerImageConfig = {
    type: number
    config: ImageConfig
  }
  export interface Image {
    id: number
    name: string
    state: number
    functions: Array<number>
    configs: Array<DockerImageConfig>
    url: string
    description: string
    createTime: string
    objectType: ObjectType
    related?: Array<Image>
    liveCode?: boolean
    errorCode?: string
  }

  export interface ImageList {
    items: Image[]
    total: number
  }

  type ResultType = 'dataset' | 'model'
  export interface Iteration {
    id: number
    projectId: number
    name?: string
    round: number
    currentStep?: Step
    steps: Step[]
    testSet: DatasetId
    wholeMiningSet: DatasetId
    prevIteration?: number
    model?: Model
    end: boolean
  }

  export interface Step {
    id: number
    finished?: boolean
    name: string
    percent?: number
    preSetting?: PlainObject
    state?: number
    taskId?: number
    taskType?: number
    resultType?: ResultType
    resultId?: number
  }

  export interface PageStep extends Step {
    label: string
    value: string
    current?: string
    selected?: string
    index?: number
    act?: string
    react?: string
    next?: string
    end?: boolean
    unskippable?: boolean
  }

  interface ShareImage {
    docker_name: string
    functions?: string
    contributor?: string
    organization?: string
    description?: string
  }

  type PlainObject = {
    [key: string]: any
  }

  export interface Task<P = TaskParams> {
    name: string
    type: number
    project_id: number
    is_deleted: number
    create_datetime: string
    update_datetime: string
    id: number
    hash: string
    state: number
    error_code: string
    duration: number
    percent: number
    parameters: P
    config: PlainObject
    result_type: number
    is_terminated: boolean
  }

  type MergeStrategy = 0 | 1 | 2
  type MiningStrategy = 0 | 1 | 2
  type Preprocess = {
    [func: string]: PlainObject
  }

  type ProgressTask = {
    hash: string
    result_state: number
    percent: number
    state: number
    reload?: boolean
  }

  type TaskParams = FusionParams | FilterParams | MergeParams | TrainingParams | LabelParams | MiningParams | InferenceParams

  interface Params {
    dataset_id: DatasetId
    dataset_group_id?: number
    dataset_group_name?: string
    description?: string
  }

  interface DockerParams extends Params {
    docker_image_id: ImageId
    docker_image_config: ImageConfig
    labels: Labels
    model_id?: ModelId
    model_stage_id?: StageId
    gpuCount?: number
    config?: PlainObject
  }

  interface FilterParams extends Params {
    include_labels?: Labels
    exclude_labels?: Labels
    sampling_count?: number
  }
  interface FusionParams extends Params {
    iteration_id?: number
    iteration_stage?: number
    exclude_last_result?: boolean
    include_datasets?: DatasetId[]
    exclude_datasets?: DatasetId[]
    mining_strategy?: MiningStrategy
    merge_strategy?: MergeStrategy
    include_labels?: Labels
    exclude_labels?: Labels
    sampling_count?: number
  }

  interface MergeParams extends Params {
    include_datasets?: DatasetId[]
    exclude_datasets?: DatasetId[]
    merge_strategy?: MergeStrategy
  }

  interface LabelParams extends Params {
    labels: Labels
    extra_url?: string
    annotation_type: 0 | 1 | 2
  }

  interface TrainingParams extends DockerParams {
    validation_dataset_id: DatasetId
    strategy: number
    preprocess: Preprocess
  }

  interface MiningParams extends DockerParams {
    top_k: number
    generate_annotations?: boolean
  }

  interface InferenceParams extends DockerParams {}

  type KeywordsCount = {
    keywords: string[]
    count: {
      [keyword: string]: number
    }
  }
  type MiningStats = {
    totalList: KeywordsCount
    keywordList: KeywordsCount
  }
}
