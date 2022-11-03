import { ColumnType } from "antd/lib/table"

import StrongTitle from "./StrongTitle"
import RenderProgress from "@/components/common/Progress"
import { Result } from "@/interface/common"

function State<T extends Result> (): ColumnType<T> {
  return {
  title: StrongTitle('dataset.column.state'),
  dataIndex: 'state',
  render: (state, record) => RenderProgress(state, record),
}}

export default State
