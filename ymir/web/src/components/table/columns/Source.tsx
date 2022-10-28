import { ColumnType } from "antd/lib/table"

import StrongTitle from "./StrongTitle"
import TypeTag from "@/components/task/TypeTag"
import { Result } from "@/interface/common"

const Source: ColumnType<Result> = {
  title: StrongTitle("dataset.column.source"),
  dataIndex: "taskType",
  render: (type) => <TypeTag type={type} />,
  sorter: (a, b) => a.taskType - b.taskType,
  ellipsis: true,
}

export default Source
