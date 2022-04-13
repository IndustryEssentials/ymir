import { Modal, Form, Input, Select, message, Button } from "antd"
import { forwardRef, useEffect, useState, useImperativeHandle } from "react"
import { connect } from 'dva'

import t from '@/utils/t'
import { TASKTYPES } from "@/constants/task"
import Confirm from "@/components/common/dangerConfirm"

const Terminate = forwardRef(({ stopTask, ok = () => { } }, ref) => {
  const [visible, setVisible] = useState(false)
  const [id, setId] = useState(null)
  const [name, setName] = useState('')
  const [type, setType] = useState(null)
  const [result, setResult] = useState({})

  useEffect(() => {
    id && terminate()
  }, [id])

  useImperativeHandle(ref, () => ({
    confirm: (result) => {
      const name = result.name + result.versionName
      const { id, type } = result.task
      setResult(result)
      setId(id)
      setName(name)
      setType(type)
    }
  }), [])

  function terminate() {
    saveResult() ? terminateWithData() : terminateNoData()
  }

  function terminateNoData() {
    Confirm({
      content: t("task.action.terminate.confirm.content", { name }),
      onOk: terminateTask,
      onCancel: cancel,
      okText: t('task.action.terminate'),
    })
  }

  function terminateWithData() {
    setVisible(true)
  }

  async function terminateTask(withData = false) {
    const result = await stopTask(id, withData)
    handle(result)
  }

  function cancel() {
    setId(null)
    setVisible(false)
  }

  function handle(res) {
    if (res) {
      ok(res, result)
    }
    setVisible(false)
    setId(null)
  }

  function saveResult() {
    return [TASKTYPES.TRAINING, TASKTYPES.LABEL].indexOf(type) > -1
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
      {t("task.action.terminate.confirm.content", { name })}
    </Modal>
  )
})

const props = (state) => {
  return {
    username: state.user.username,
  }
}
const actions = (dispatch) => {
  return {
    stopTask(id, with_data) {
      return dispatch({
        type: 'task/stopTask',
        payload: { id, with_data },
      })
    },
  }
}
export default connect(props, actions, null, { forwardRef: true })(Terminate)
