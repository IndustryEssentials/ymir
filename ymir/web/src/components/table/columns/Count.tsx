import { ColumnType } from "antd/lib/table"

import { Dataset } from "@/interface/dataset"
import { humanize } from "@/utils/number"
import StrongTitle from "./StrongTitle"

const Count: ColumnType<Dataset> = {
  title: StrongTitle("dataset.column.asset_count"),
  dataIndex: "assetCount",
  render: (num) => humanize(num),
  sorter: (a, b) => a.assetCount - b.assetCount,
  width: 120,
}

export default Count
