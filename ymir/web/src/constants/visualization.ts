import { Visualization } from "@/interface/visualization"
import { BackendData } from "@/interface/common"
import { format } from '@/utils/date'

export function transferVisualization(data: BackendData): Visualization {
  return {
    id: data.id,
    userId: data.user_id,
    tid: data.tid,
    tasks: data.tasks,
    createTime: format(data.create_datetime),
    updateTime: format(data.update_datetime),
  }
}