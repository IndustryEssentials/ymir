import t from "@/utils/t"
import CheckboxSelector from "./checkboxSelector"

const types = [
  { label: 'annotation.gt', value: 'gt', checked: true, },
  { label: 'annotation.pred', value: 'pred', },
]

const GtSelector = props => <CheckboxSelector
  options={types.map(type => ({ ...type, label: t(type.label)}))}
  label={t('dataset.assets.selector.gt.label')}
  {...props}
/>

export default GtSelector
