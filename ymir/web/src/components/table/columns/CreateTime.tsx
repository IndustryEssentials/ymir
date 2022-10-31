import { ColumnType } from "antd/lib/table"

import { diffTime } from '@/utils/date'
import StrongTitle from "./StrongTitle"
import { Result } from "@/interface/common"
import { Dataset, InferDataset } from "@/interface/dataset"
import { ModelVersion } from "@/interface/model"

function CreateTime<T extends Result>(): ColumnType<T> {
  return {
    title: StrongTitle("dataset.column.create_time"),
    dataIndex: "createTime",
    sorter: (a: T, b: T) => diffTime(a.createTime, b.createTime),
    sortDirections: ['ascend', 'descend', 'ascend'],
    defaultSortOrder: 'descend',
    width: 180,
  }
}

export default CreateTime
