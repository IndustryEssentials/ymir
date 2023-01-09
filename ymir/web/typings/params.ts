declare namespace YParams {
  type ResultListQuery = {
    pid?: number
    gid?: number
    type?: number | string
    objectType?: number
    state?: number
    name?: string
    limit?: number
    offset?: number
    startTime?: string | number
    endTime?: string | number
    visible?: boolean
    desc?: boolean
  }

  interface DatasetsQuery extends ResultListQuery {
    orderBy?: 'id' | 'create_datetime' | 'asset_count' | 'source'
    keywords?: string[]
  }

  interface ModelsQuery extends ResultListQuery {
    orderBy?: 'id' | 'create_datetime' | 'update_datetime' | 'map' | 'source'
  }

  type DatasetQuery = {
    did: number
    pid?: number
    keywords?: string[]
  }

  type GroupsQuery = {
    name?: string
    offset?: number
    limit?: number
  }

  interface AssetQueryParams extends DatasetsQuery {
    id: number
    cm?: number[]
    annoType?: number[]
    type?: string
  }

  interface EvaluationParams extends DatasetsQuery {
    datasets: number[]
    confidence: number
    iou: number
    averageIou: boolean
    ck: string
  }

  interface DatasetCreateParams {
    name: string
    pid: number
    url?: string
    did?: number
    path?: string
    strategy?: number
    description?: string
  }

  interface ModelCreateParams {
    projectId: number
    name: string
    description?: string
    url?: string
    path?: string
    modelId?: number
  }
  interface ModelVerifyParams {
    projectId: number
    modelStage: [number, number]
    urls: string[]
    image: string
    config: { [key: string]: any }
  }
}
