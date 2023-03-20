import { useRef } from "react"
import { Button, Col, Descriptions, Progress, Row } from "antd"

import t from "@/utils/t"
import { toFixed } from "@/utils/number"
import Terminate from "./terminate"
import { ResultStates } from "@/constants/common"
import { TASKSTATES } from "@/constants/task"
import StateTag from "@/components/task/StateTag"
import s from "./detail.less"

const { Item } = Descriptions

const labelStyle = {
  width: "15%",
  paddingRight: "20px",
  justifyContent: "flex-end",
}

function TaskProgress({ state, result = {}, task = {}, fresh = () => { }, progress = 0, duration = "" }) {
  const terminateRef = useRef(null)

  function terminate() {
    terminateRef.current.confirm(result)
  }

  function terminateVisible() {
    const resultReady = state === ResultStates.READY
    const isTerminated = task.is_terminated
    const isPending = task.state === TASKSTATES.PENDING
    return !isPending && resultReady && !isTerminated
  }

  function terminateOk() {
    fresh()
  }

  return (
    <div className='taskDetail'>
      <Descriptions
        bordered
        labelStyle={labelStyle}
        title={<div className='title'>{t("task.detail.state.title")}</div>}
        className='infoTable'
      >
        <Item label={t("task.detail.state.current")}>
          <Row>
            <Col>
              {task.is_terminated && state === ResultStates.READY ? t('task.state.terminating') : <>
                <StateTag state={state} code={task.error_code} />
                {state === ResultStates.VALID
                  ? t("task.column.duration") + ": " + duration
                  : null}
              </>}
            </Col>
            <Col hidden={state !== ResultStates.READY} flex={1}>
              <Progress
                style={{ width: '90%'}}
                strokeColor={"#FAD337"}
                percent={toFixed(progress * 100, 2)}
              />
            </Col>
            <Col hidden={!terminateVisible()}>
              <Button onClick={() => terminate(task)}>
                {t("task.action.terminate")}
              </Button>
            </Col>
          </Row>
        </Item>
      </Descriptions>
      <Terminate ref={terminateRef} ok={terminateOk} />
    </div>
  )
}

export default TaskProgress
