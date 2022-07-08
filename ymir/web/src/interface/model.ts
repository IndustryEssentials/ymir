import { Result } from "@/interface/common"

export interface Stage {
  id: number,
  name: string,
  map: number,
  modelId?: number,
  modelName?: string,
}
export interface ModelGroup {
  id: number,
  projectId: number,
  name: string,
  createTime: string,
}
export interface ModelVersion extends Result {
  map: number,
  url: string,
  stages?: Array<Stage>,
  recommendStage: number,
}
