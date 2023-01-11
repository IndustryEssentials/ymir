import { runningModel, validModel } from '@/constants/model'
import { useHistory } from 'umi'
import { ShieldIcon, VectorIcon, EditIcon, FileDownloadIcon, TrainIcon, WajueIcon, StopIcon, BarchartIcon } from '@/components/common/Icons'
import { getDeployUrl, getTensorboardLink } from '@/constants/common'
import t from '@/utils/t'
import { TASKSTATES, TASKTYPES } from '@/constants/task'
import usePublish from './usePublish'
import { ReactElement, ReactNode } from 'react'

type FuncParams = {
  [key: string]: (model: YModels.Model) => void
}

type ListActionsType = (funcs: FuncParams) => (model: YModels.Model) => YComponents.Action[]

const useListActions: ListActionsType = ({ stop, editDesc }) => {
  const history = useHistory()
  const [publish] = usePublish()

  const getActions = (record: YModels.Model) => {
    const { id, projectId: pid, name, url, state, taskState, taskType, task, isProtected, stages, recommendStage } = record
    const valid = validModel(record)
    const running = runningModel(record)
    const actions = [
      {
        key: 'publish',
        label: t('model.action.publish'),
        hidden: () => !valid || !getDeployUrl(),
        onclick: () => publish(record),
        icon: <ShieldIcon />,
      },
      {
        key: 'verify',
        label: t('model.action.verify'),
        hidden: () => !valid,
        onclick: () => history.push(`/home/project/${pid}/model/${id}/verify`),
        icon: <ShieldIcon />,
      },
      {
        key: 'download',
        label: t('model.action.download'),
        link: url,
        target: '_blank',
        hidden: () => !valid,
        icon: <FileDownloadIcon />,
      },
      {
        key: 'mining',
        label: t('dataset.action.mining'),
        hidden: () => !valid,
        onclick: () => history.push(`/home/project/${pid}/mining?mid=${id},${recommendStage}`),
        icon: <VectorIcon />,
      },
      {
        key: 'train',
        label: t('dataset.action.train'),
        hidden: () => !valid,
        onclick: () => history.push(`/home/project/${pid}/train?mid=${id},${recommendStage}`),
        icon: <TrainIcon />,
      },
      {
        key: 'inference',
        label: t('dataset.action.inference'),
        hidden: () => !valid,
        onclick: () => history.push(`/home/project/${pid}/inference?mid=${id},${recommendStage}`),
        icon: <WajueIcon />,
      },
      {
        key: 'edit.desc',
        label: t('common.action.edit.desc'),
        onclick: () => editDesc(record),
        icon: <EditIcon />,
      },
      {
        key: 'stop',
        label: t('task.action.terminate'),
        onclick: () => stop(record),
        hidden: () => taskState === TASKSTATES.PENDING || !running || task.is_terminated,
        icon: <StopIcon />,
      },
      {
        key: 'tensor',
        label: t('task.action.training'),
        target: '_blank',
        link: getTensorboardLink(task.hash),
        hidden: () => taskType !== TASKTYPES.TRAINING,
        icon: <BarchartIcon />,
      },
      // {
      //   key: 'hide',
      //   label: t('common.action.hide'),
      //   onclick: () => hide(record),
      //   hidden: () => hideHidden(record),
      //   icon: <EyeOffIcon />,
      // },
    ]
    return actions
  }
  return getActions
}

export default useListActions
