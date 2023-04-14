import { CSSProperties, FC, useEffect, useState } from 'react'

import { Message } from '@/constants'
import useRequest from '@/hooks/useRequest'
import { STATES } from '@/constants/image'
import { isImage } from '@/constants/TaskResultType'
import { ResultStates, validState } from '@/constants/common'
import { getTaskTypeLabel, TASKTYPES } from '@/constants/task'
import t from '@/utils/t'

import { getRecommendStage } from '@/constants/model'
import { percent } from '@/utils/number'
import { useHistory } from 'umi'

export type Props = {
  title: string
  content: string
  go: () => void
  unread: () => void
}

const BaseItem = (Template: FC<Props>) => {
  const RenderItem: FC<{ message?: Message }> = ({ message }) => {
    const history = useHistory()
    const [title, setTitle] = useState('')
    const [content, setContent] = useState('')
    const { run: readMessage } = useRequest<null, [id: number]>('message/readMessage', {
      loading: false,
    })

    useEffect(() => {
      if (!message) {
        setTitle('')
        setContent('')
        return
      }
      let typeLabel = t(getTaskTypeLabel(message.taskType))

      setTitle(getTitle(message, typeLabel))
      setContent(getContent(message, typeLabel))
    }, [message])

    const getTitle = (msg: Message, typeLabel: string) => {
      let stateLabel = ''
      if (isImage(msg.type)) {
        stateLabel = getImageStateLabel(msg.resultState as STATES)
      } else {
        stateLabel = getStateLabel(msg.resultState as ResultStates)
      }

      return `${typeLabel}${stateLabel}`
    }

    const getContent = (message: Message, typeLabel: string) => {
      const { taskType, resultState, result } = message

      const renderObject = {
        type: typeLabel,
        state: isImage(message.resultState) ? getImageStateLabel(resultState as STATES) : getStateLabel(resultState as ResultStates),
        name: getName(message),
        metricLabel: '',
        metric: '',
      }

      switch (taskType) {
        case TASKTYPES.TRAINING:
        case TASKTYPES.MODELIMPORT:
          const model = result as YModels.Model
          if (model) {
            const stage = getRecommendStage(model)
            renderObject['metricLabel'] = stage?.primaryMetricLabel || ''
            renderObject['metric'] = percent(stage?.primaryMetric || 0) || ''
          }
          return t(`message.content.model.${getState(validState(resultState))}`, renderObject)
        default:
          return t('message.content.common', renderObject)
      }
    }

    const getState = (valid: boolean) => (valid ? 'finish' : 'failure')

    const getStateLabel = (state: ResultStates) => t(`task.state.${getState(validState(state))}`)
    const getImageStateLabel = (state: STATES) => t(`task.state.${getState(state === STATES.DONE)}`)
    const getName = (message: Message) => {
      if (!message.result) {
        return ''
      }
      return `${message.result.name}`
    }

    const go = () => {
      if (!message) {
        return
      }
      history.push(`/home/project/${message?.pid}/${message?.resultModule}/${message?.resultId}`)
      unread()
    }

    const unread = () => {
      message?.id && readMessage(message.id)
    }

    return <Template key={message?.id} title={title} content={content} go={go} unread={unread} />
  }
  return RenderItem
}

export default BaseItem
