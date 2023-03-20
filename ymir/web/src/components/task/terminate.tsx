import { Modal, Form, Input, Select, message, Button } from 'antd'
import { forwardRef, useEffect, useState, useImperativeHandle } from 'react'

import t from '@/utils/t'
import { TASKTYPES } from '@/constants/task'
import confirmConfig from '@/components/common/DangerConfirm'
import useRequest from '@/hooks/useRequest'
import { FC } from 'react'
type Result = YModels.Result & {
  task: YModels.Task
}

type Props = {
  ok: (resultTask: YModels.Task, result: Result) => void
}
export type RefProps = {
  confirm: (result: Result) => void
}
const Terminate = forwardRef<RefProps, Props>(({ ok }, ref) => {
  const [visible, setVisible] = useState(false)
  const [id, setId] = useState<number>()
  const [name, setName] = useState('')
  const [type, setType] = useState<number>()
  const [result, setResult] = useState<Result>()
  const { runAsync: stopTask } = useRequest<YModels.Task, [{ id: number; with_data?: boolean }]>('task/stopTask')

  useEffect(() => {
    id && terminate()
  }, [id])

  useImperativeHandle(
    ref,
    () => ({
      confirm: (result: Result) => {
        const name = result.name + result.versionName
        const { id, type } = result.task
        setResult(result)
        setId(id)
        setName(name)
        setType(type)
      },
    }),
    [],
  )

  function terminate() {
    saveResult() ? terminateWithData() : terminateNoData()
  }

  function terminateNoData() {
    Modal.confirm(
      confirmConfig({
        content: t('task.action.terminate.confirm.content', { name }),
        onOk: terminateTask,
        onCancel: cancel,
        okText: t('task.action.terminate'),
      }),
    )
  }

  function terminateWithData() {
    setVisible(true)
  }

  async function terminateTask(withData = false) {
    if (!id) {
      return
    }
    const result = await stopTask({ id, with_data: withData })
    handle(result)
  }

  function cancel() {
    setId(undefined)
    setVisible(false)
  }

  function handle(res: YModels.Task) {
    if (res && result) {
      ok(res, result)
    }
    setVisible(false)
    setId(undefined)
  }

  function saveResult() {
    return type && [TASKTYPES.TRAINING, TASKTYPES.LABEL].indexOf(type) > -1
  }

  return (
    <Modal
      visible={visible}
      onCancel={cancel}
      footer={[
        <Button key="nodata" type="primary" onClick={() => terminateTask()}>
          {t('task.terminate.label.nodata')}
        </Button>,
        <Button key="withdata" type="primary" onClick={() => terminateTask(true)}>
          {t('task.terminate.label.withdata')}
        </Button>,
      ]}
    >
      {t('task.action.terminate.confirm.content', { name })}
    </Modal>
  )
})

export default Terminate
