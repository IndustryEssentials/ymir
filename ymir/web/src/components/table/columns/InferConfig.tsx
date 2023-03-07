import { Popover, TableColumnType } from 'antd'
import ReactJson from 'react-json-view'

import StrongTitle from './StrongTitle'
import t from '@/utils/t'

const title = 'model.diagnose.label.config'
const InferConfig = <T extends YModels.Prediction>(): TableColumnType<T> => ({
  title: <StrongTitle label={title} />,
  dataIndex: 'inferConfig',
  render: (config) => {
    const content = <ReactJson src={config} name={false} />
    const label = t(title)
    return (
      <Popover content={content}>
        <span title={label}>{label}</span>
      </Popover>
    )
  },
})

export default InferConfig
