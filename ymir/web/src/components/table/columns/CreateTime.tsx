import { ColumnType } from "antd/lib/table"

import { Result } from "@/interface/common"
import { diffTime } from '@/utils/date'
import StrongTitle from "./StrongTitle"

const CreateTime: ColumnType<Result> = {
  title: StrongTitle("dataset.column.create_time"),
  dataIndex: "createTime",
  sorter: (a, b) => diffTime(a.createTime, b.createTime),
  sortDirections: ['ascend', 'descend', 'ascend'],
  defaultSortOrder: 'descend',
  width: 180,
}

export default CreateTime
