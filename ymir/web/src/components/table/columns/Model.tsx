import { ColumnType } from "antd/lib/table"
import { Tooltip } from "antd"

import { InferDataset } from "@/interface/dataset"
import StrongTitle from "./StrongTitle"
import t from '@/utils/t'
import { validDataset } from '@/constants/dataset'

const Model: ColumnType<InferDataset> = {
  title: StrongTitle("dataset.column.model"),
  dataIndex: "model",
  render: (_, dataset) => {
    
    return dataset
  },
}

export default Model
