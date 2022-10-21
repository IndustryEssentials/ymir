import React, {  } from "react"
import { Button, Form, Space } from "antd"

import t from "@/utils/t"


function BottomButtons({
  mode='normal',
  fromIteration = false,
  stage,
  result,
  stepState = 'start',
  label = 'common.confirm',
  ok = () => { },
  next = () => {},
  skip = () => { },
  update = () => { }
}) {

  const currentStage = () => stage.value === stage.current
  const finishStage = () => stage.value < stage.current
  const pendingStage = () => stage.value > stage.current

  const isPending = () => state < 0
  const isReady = () => state === states.READY
  const isValid = () => state === states.VALID
  const isInvalid = () => state === states.INVALID

  // !stage.unskippable && !end && currentStage()
  const skipBtn = <Form.Item name='skip' noStyle>
    <Button size="large" onClick={skip}>
      {t('common.skip')}
    </Button>
  </Form.Item>

  const confirmBtn = <Form.Item name='submitBtn' noStyle>
    <Button type="primary" size="large" htmlType="submit">
      {t(label)}
    </Button>
  </Form.Item>

  const backBtn = <Form.Item name='backBtn' noStyle>
    <Button size="large" onClick={() => history.goBack()}>
      {t('common.step.next')}
    </Button>
  </Form.Item>

  const nextBtn = <Form.Item name='nextBtn' noStyle>
    <Button size="large" onClick={next}>
      {t('task.btn.back')}
    </Button>
  </Form.Item>

  return (
    <Form.Item wrapperCol={{ offset: 8 }}>
      <Space size={20}>
        {mode === 'iteration' ? <>
          {stepState === 'start' ? confirmBtn : null}
          {stepState === 'finish' ? nextBtn: null}
          {skipBtn}
        </> : <>
          {confirmBtn}
          {backBtn}
        </>
        }
      </Space>
    </Form.Item>
  )
}

export default BottomButtons
