import EvaluationSelector from '@/components/form/EvaluationSelector'
import KeywordSelector, { ValueType } from '@/components/form/KeywordFilter'
import { Col, Row, Space } from 'antd'
import { FC, useEffect, useState } from 'react'
import DatasetInfo from './DatasetInfo'
import ListColumnCountSelect from './ListColumnCountSelect'
import ListVisualSelect from './ListVisualSelect'
import styles from '../assets.less'
import { isDetection } from '@/constants/objectType'
import VisualModes from './VisualModes'

export type FormValues = {
  columns?: number
  mode?: number
  evaluation?: number
  keywords?: ValueType
}
type Props = {
  current?: YModels.Dataset | YModels.Prediction
  initialValues?: FormValues
  onChange?: (value: FormValues) => void
  isPred?: boolean
}

const AssetsTitle: FC<Props> = ({ isPred, current, initialValues, onChange }) => {
  const [values, setValues] = useState<FormValues>({
    mode: isPred ? VisualModes.All : VisualModes.Gt,
    columns: 5,
  })

  useEffect(() => {
    initialValues && setValues(initialValues)
  }, [initialValues])

  useEffect(() => onChange && onChange(values), [values])

  const changeValue = (value: FormValues[keyof FormValues], field: keyof FormValues) => setValues((values) => ({ ...values, [field]: value }))
  return (
    <Row className={styles.labels}>
      <Col flex={1}>
        <DatasetInfo dataset={current} />
      </Col>
      <Col>
        <ListColumnCountSelect value={values.columns} onChange={(value) => changeValue(value, 'columns')} />
      </Col>
      <Col span={24} style={{ fontSize: 14, textAlign: 'right', marginTop: 10 }}>
        <Space size={20} wrap={true} style={{ textAlign: 'left' }}>
          <ListVisualSelect
            value={values.mode}
            style={{ width: 200 }}
            pred={isPred}
            seg={!isDetection(current?.type)}
            onChange={(value) => changeValue(value, 'mode')}
          />
          {isPred && current?.evaluated ? (
            <EvaluationSelector value={values.evaluation} onChange={({ target }) => changeValue(target.value, 'evaluation')} />
          ) : null}
          <KeywordSelector value={values.keywords} onChange={(value) => changeValue(value, 'keywords')} dataset={current} />
        </Space>
      </Col>
    </Row>
  )
}

export default AssetsTitle
