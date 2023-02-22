import React from 'react'
import t from '@/utils/t'
import CheckboxSelector, { Props} from './CheckboxSelector'

const types = [
  { label: 'annotation.gt', value: 'gt' },
  { label: 'annotation.pred', value: 'pred' },
]

const GtSelector: React.FC<Omit<Props, 'options'>> = (props) => (
  <CheckboxSelector {...props} label={t('dataset.assets.selector.gt.label')} options={types.map((type) => ({ ...type, label: t(type.label) }))} />
)

export default GtSelector
