import React, { } from "react"
import { Button, Form, Space } from "antd"

import t from "@/utils/t"
import { validState, invalidState, readyState } from '@/constants/common'

function Buttons({
  step,
  state,
  next = () => { },
  skip = () => { },
  react = () => { },
}) {
  const actLabel = t(step.act)
  const reactLabel = t(step.react)
  const end = !step.next
  const finished = step.value < step.current
  const current = step.value === step.current
  const pending = step.value > step.current

  const stepPending = state < 0
  const retry = state === -2

  const skipBtn = !step.unskippable && !end && current ? <Form.Item name='skip' noStyle>
    <Button size="large" onClick={skip}>
      {t('common.skip')}
    </Button>
  </Form.Item> : null

  const confirmBtn = current && stepPending ? <Form.Item name='submitBtn' noStyle>
    <Button type="primary" size="large" htmlType="submit">
      {retry ? reactLabel : actLabel}
    </Button>
  </Form.Item> : null

  const nextBtn = retry || (current && validState(state)) ? <Form.Item name='nextBtn' noStyle>
    <Button type="primary" size="large" onClick={next}>
      {t('common.step.next')}
    </Button>
  </Form.Item> : null

  const reactBtn = current && (validState(state) || invalidState(state)) ? <Form.Item name='nextBtn' noStyle>
    <Button type="primary" size="large" onClick={react}>
      {reactLabel}
    </Button>
  </Form.Item> : null

  return (
    <Space size={20}>
      {confirmBtn}
      {reactBtn}
      {nextBtn}
      {skipBtn}
    </Space>
  )
}

export default Buttons
