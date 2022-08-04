import { BackendData } from "@/interface/common"
export interface Visualization {
  id: number,
  userId: number,
  tid: string,
  tasks?: Array<BackendData>,
  iou: number,
  confidence: number,
  createTime: string,
  updateTime: string,
}