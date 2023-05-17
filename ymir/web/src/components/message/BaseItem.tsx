import { FC, useEffect, useState } from 'react'

import { Message, Model } from '@/constants'
import useRequest from '@/hooks/useRequest'
import { ResultStates, validState } from '@/constants/common'
import { getTaskTypeLabel, TASKTYPES } from '@/constants/task'
import t from '@/utils/t'

import { getRecommendStage } from '@/constants/model'
import { percent } from '@/utils/number'
import { useHistory, useSelector } from 'umi'
import { getDetailPage } from '@/services/common'

export type Props = {
  total: number
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
    const total = useSelector(({ message }) => message.total)
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
      let stateLabel = getStateLabel(msg.resultState)

      return `${typeLabel}${stateLabel}`
    }

    const getContent = (message: Message, typeLabel: string) => {
      const { taskType, resultState, result } = message

      const renderObject = {
        type: typeLabel,
        state: getStateLabel(resultState),
        name: getName(message),
        metricLabel: '',
        metric: '',
      }

      switch (taskType) {
        case TASKTYPES.TRAINING:
        case TASKTYPES.MODELIMPORT:
          const model = result as Model
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
    const getName = (message: Message) => {
      if (!message.result) {
        return ''
      }
      return message.result.name ? `${message.result.name}` : ''
    }

    const go = () => {
      if (!message) {
        return
      }
      const url =
        message.resultModule === 'prediction' ? `/home/project/${message.pid}/prediction` : getDetailPage(message.resultModule, message.resultId, message.pid)
      history.push(url)
      unread()
    }

    const unread = () => {
      message?.id && readMessage(message.id)
    }

    return message ? <Template key={message.id} total={total} title={title} content={content} go={go} unread={unread} /> : null
  }
  return RenderItem
}

export default BaseItem
