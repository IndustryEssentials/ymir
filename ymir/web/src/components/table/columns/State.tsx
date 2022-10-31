import { ColumnType } from "antd/lib/table"

import StrongTitle from "./StrongTitle"
import RenderProgress from "@/components/common/Progress"

const State: ColumnType<any> = {
  title: StrongTitle('dataset.column.state'),
  dataIndex: 'state',
  render: (state, record) => RenderProgress(state, record),
}

export default State
