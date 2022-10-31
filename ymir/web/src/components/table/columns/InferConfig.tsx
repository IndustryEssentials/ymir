import { ColumnType } from "antd/lib/table"

import StrongTitle from "./StrongTitle"
import { InferDataset } from '@/interface/dataset'
import ReactJson from 'react-json-view'
import { Popover } from "antd"

const InferConfig = <T extends InferDataset>(): ColumnType<T> => ({
  title: StrongTitle("dataset.column.model"),
  dataIndex: "inferConfig",
  render: (config) => {
    const content = <ReactJson src={config} name={false} />
    const label = `Inference Config`
    return <Popover content={content}>
      <span title={label}>{label}</span>
    </Popover>
  },
})

export default InferConfig
