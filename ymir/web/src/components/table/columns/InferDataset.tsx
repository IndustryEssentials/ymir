import { ColumnType } from "antd/lib/table"

import StrongTitle from "./StrongTitle"
import { InferDataset as DatasetType } from '@/interface/dataset'
import VersionName from '@/components/result/VersionName'
import { Link } from "umi"

const InferDataset = <T extends DatasetType>(): ColumnType<T> => ({
  title: StrongTitle("dataset.column.model"),
  dataIndex: "model",
  render: (_, { projectId, inferDatasetId, inferDataset }) => {
    const label = inferDataset ? <VersionName result={inferDataset} /> : inferDatasetId
    return <Link to={`/home/project/${projectId}/dataset/${inferDatasetId}`}>{label}</Link>
  },
})

export default InferDataset
