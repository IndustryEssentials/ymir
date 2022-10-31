import { Group, Result } from "@/interface/common"

export interface Stage {
  id: number,
  name: string,
  map: number,
  modelId?: number,
  modelName?: string,
}
export interface ModelGroup extends Group { }
export interface ModelVersion extends Result {
  map: number,
  url: string,
  stages?: Array<Stage>,
  recommendStage: number,
}
