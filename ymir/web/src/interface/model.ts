
export interface ModelGroup {
  id: number,
  name: string,
  createTime: string,
}

export interface ModelVersion {
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


export interface OriginModelGroup {
  id: number,
  name: string,
  create_datetime: string,
}

export interface OriginModelVersion {
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
