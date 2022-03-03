
export interface DatasetGroup {
  id: number,
  name: string,
  createTime: string,
}

export interface DatasetVersion {
  id: number,
  name: string,
  version: number,
  keywords: Array<string>,
  state: number,
  createTime: string,
  assetCount: number,
  taskId: number,
  progress: number,
  taskState: number,
}


export interface OriginDatasetGroup {
  id: number,
  name: string,
  create_datetime: string,
}

export interface OriginDatasetVersion {
  id: number,
  name: string,
  version: number,
  keywords: Array<string>,
  state: number,
  create_datetime: string,
  asset_count: number,
  task_id: number,
  progress: number,
  taskState: number,
}
