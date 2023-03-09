import { FC, useEffect, useState } from 'react'
import { Form, Select, SelectProps } from 'antd'
import { isDetection } from '@/constants/objectType'
import t from '@/utils/t'

type Props = SelectProps & {
  prediction?: YModels.Prediction
}

const CKSelector: FC<Props> = ({ prediction }) => {
  if (!isDetection(prediction?.type)) {
    return null
  }
  const [cks, setCks] = useState<string[]>([])

  useEffect(() => {
    const cks = prediction?.cks?.keywords.map(({ keyword }) => keyword)
    cks?.length && setCks(cks)
  }, [prediction])
  return (
    <Form.Item label={t('keyword.ck.label')} name="ck">
      <Select options={cks.map((ck) => ({ value: ck, label: ck }))} allowClear></Select>
    </Form.Item>
  )
}

export default CKSelector
