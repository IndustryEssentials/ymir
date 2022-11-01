import { ColumnType } from "antd/lib/table"

import StrongTitle from "./StrongTitle"
import { InferDataset } from '@/interface/dataset'
import ModelVersionName from '@/components/result/ModelVersionName'
import { Link } from "umi"

const Model = <T extends InferDataset>(): ColumnType<T> => ({
  title: StrongTitle("dataset.column.model"),
  dataIndex: "model",
  render: (_, { projectId, inferModel, inferModelId }) => {
    const label = inferModel ? <ModelVersionName result={inferModel} stageId={inferModelId[1]} /> : inferModelId.join(',')
    return <Link to={`/home/project/${projectId}/model/${inferModelId[0]}`}>{label}</Link>
  },
})

export default Model
