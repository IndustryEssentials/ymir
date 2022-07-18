import { Visualization } from "@/interface/visualization"
import { BackendData } from "@/interface/common"
import { format } from '@/utils/date'

export function transferVisualization(data: BackendData): Visualization {
  return {
    id: data.id,
    userId: data.user_id,
    tid: data.tid,
    tasks: data.tasks,
    iou: data.iou_thr,
    confidence: data.conf_thr,
    createTime: format(data.create_datetime),
    updateTime: format(data.update_datetime),
  }
}