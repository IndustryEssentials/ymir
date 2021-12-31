import { Modal, Form, Input, Select, message, Button } from "antd"
import { forwardRef, useEffect, useState, useImperativeHandle } from "react"
import { connect } from 'dva'

import t from '@/utils/t'
import { TASKTYPES } from "@/constants/task"
import Confirm from "@/components/common/dangerConfirm"
import { TASKSTATES } from "../../../constants/task"

const Terminate = forwardRef(({ stopTask, ok = () => { } }, ref) => {
  const [visible, setVisible] = useState(false)
  const [id, setId] = useState(null)
  const [name, setName] = useState('')
  const [type, setType] = useState(null)
  const [state, setState] = useState(null)

  useEffect(() => {
    id && terminate()
  }, [id])

  useImperativeHandle(ref, () => ({
    confirm: ({ id, name, type, state }) => {
      setId(id)
      setName(name)
      setType(type)
      setState(state)
    }
  }), [])

  function terminate() {
    saveResult() ? terminateWithData() : terminateNoData()
  }

  function terminateNoData() {
    console.log('terminate no data')
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

  function handle(result) {
    if (result) {
      ok()
    }
    setVisible(false)
    setId(null)
  }

  function saveResult() {
    return state !== TASKSTATES.PENDING && [TASKTYPES.TRAINING, TASKTYPES.LABEL].indexOf(type) > -1
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
