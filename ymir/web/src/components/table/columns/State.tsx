import { ColumnType } from "antd/lib/table"

import { Result } from "@/interface/common"
import StrongTitle from "./StrongTitle"
import RenderProgress from "@/components/common/Progress"

const State: ColumnType<Result> = {
  title: StrongTitle('dataset.column.state'),
  dataIndex: 'state',
  render: (state, record) => RenderProgress(state, record),
}

export default State
