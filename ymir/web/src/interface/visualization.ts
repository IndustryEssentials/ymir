import { BackendData } from "@/interface/common"
export interface Visualization {
  id: number,
  userId: number,
  tid: string,
  tasks?: Array<BackendData>,
  createTime: string,
  updateTime: string,
}