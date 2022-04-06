import { useRef } from "react"
import { Button, Col, Descriptions, Progress, Row } from "antd"

import t from "@/utils/t"
import { toFixed } from "@/utils/number"
import Terminate from "./terminate"
import { TASKSTATES } from "@/constants/task"
import { states } from "@/constants/dataset"
import StateTag from "@/components/task/stateTag"
import s from "./detail.less"

const { Item } = Descriptions

const labelStyle = {
  width: "15%",
  paddingRight: "20px",
  justifyContent: "flex-end",
}

function TaskProgress({ state, task = {}, fresh=() => {}, progress = 0, duration = "" }) {
  const terminateRef = useRef(null)

  function terminate(task) {
    terminateRef.current.confirm(task)
  }

  function terminateOk() {
    console.log('update data.')
    fresh()
  }

  return (
    <div className={s.taskDetail}>
      <Descriptions
        bordered
        labelStyle={labelStyle}
        title={<div className={s.title}>{t("task.detail.state.title")}</div>}
        className={s.infoTable}
      >
        <Item label={t("task.detail.state.current")}>
          <Row>
            <Col>
              { task.is_terminated ? t('task.state.terminated') : null}
              <StateTag state={state} />
              {state === states.VALID
                ? t("task.column.duration") + ": " + duration
                : null}
            </Col>
            <Col hidden={state !== states.READY} flex={1}>
              <Progress
                strokeColor={"#FAD337"}
                percent={toFixed(progress * 100, 2)}
              />
            </Col>
            <Col hidden={state !== states.READY}>
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
