type ResultListQuery = {
  pid?: number | string
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
  current?: number
}

interface DatasetsQuery extends ResultListQuery {
  orderBy?: 'id' | 'create_datetime' | 'asset_count' | 'source'
  keywords?: string[]
  excludeType?: number
  empty?: boolean
  haveClasses?: boolean
}

export { DatasetsQuery, ResultListQuery }
