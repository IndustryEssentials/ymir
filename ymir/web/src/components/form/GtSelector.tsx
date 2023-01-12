import React from 'react'
import t from '@/utils/t'
import CheckboxSelector from './CheckboxSelector'
import { CheckboxProps } from 'antd'

type Props = CheckboxProps

const types = [
  { label: 'annotation.gt', value: 'gt' },
  { label: 'annotation.pred', value: 'pred' },
]

const GtSelector: React.FC<Props> = (props) => (
  <CheckboxSelector options={types.map((type) => ({ ...type, label: t(type.label) }))} label={t('dataset.assets.selector.gt.label')} {...props} />
)

export default GtSelector
