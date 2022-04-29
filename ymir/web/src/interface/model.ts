import { Result } from "@/interface/common"

export interface ModelGroup {
  id: number,
  projectId: number,
  name: string,
  createTime: string,
}
export interface ModelVersion extends Result {
  map: number,
  url: string,
}
