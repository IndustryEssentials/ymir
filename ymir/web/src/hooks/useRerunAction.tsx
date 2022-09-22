import { useHistory } from "umi"
import t from "@/utils/t"
import { TASKTYPES } from '@/constants/task'
import { RefreshIcon } from "@/components/common/icons"
import { Result } from "@/interface/common"

export default function useRerunAction() {
  const history = useHistory()

  const rerun = (pid: number, type: string, record: Result) => {
    history.push({ pathname: `/home/project/${pid}/${type}`, state: { record } })
  }

  const generateRerunAction = (record: Result) => {
    const maps = {
      [TASKTYPES.TRAINING]: 'train',
      [TASKTYPES.MINING]: 'mining',
      [TASKTYPES.INFERENCE]: 'inference',
    }
    const type = maps[record.taskType]
    const pid = record.projectId
    return type ? {
      key: "rerun",
      label: t(`common.action.rerun.${type}`),
      onclick: () => rerun(pid, type, record),
      icon: <RefreshIcon />,
    } : { hidden: () => true }
  }
  return generateRerunAction
}