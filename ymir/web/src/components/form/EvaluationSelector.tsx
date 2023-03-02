import type { FC } from 'react'
import type CSS from 'csstype'
import { Col, RadioGroupProps, Row } from 'antd'

import { evaluationTags as tags } from '@/constants/dataset'
import t from '@/utils/t'
import RadioGroup from './RadioGroup'

type Props = Omit<RadioGroupProps, 'options' | 'optionType'> & {
  hidden?: boolean
  title?: string
  vertical?: boolean
  labelAlign?: CSS.Property.TextAlign
}

const types = [
  { label: 'right', value: tags.mtp },
  { label: 'fn', value: tags.fn },
  { label: 'fp', value: tags.fp },
]

const EvaluationSelector: FC<Props> = ({ vertical, hidden, labelAlign = 'left', ...props }) => (
  <Row gutter={10} hidden={hidden}>
    <Col span={vertical ? 24 : undefined} style={{ fontWeight: 'bold', textAlign: labelAlign }}>
      {t('dataset.assets.selector.evaluation.label')}
    </Col>
    <Col flex={1}>
      <RadioGroup {...props} prefix="dataset.assets.selector.evaluation." options={types} />
    </Col>
  </Row>
)

export default EvaluationSelector
