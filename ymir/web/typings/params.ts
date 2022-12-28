declare namespace YParams {
  type DatasetsQuery = {
    pid?: number
    gid?: number
    did?: number
    type?: number | string
    objectType?: number
    state?: number
    name?: string
    visible?: boolean
    limit?: number
    offset?: number
    desc?: boolean
    orderBy?: 'id' | 'create_datetime' | 'asset_count' | 'source'
    keywords?: string[]
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
}
