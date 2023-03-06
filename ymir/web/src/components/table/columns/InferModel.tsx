import { ColumnType } from 'antd/lib/table'

import StrongTitle from './StrongTitle'
import ModelVersionName from '@/components/result/ModelVersionName'
import { Link } from 'umi'

const Model = <T extends YModels.Prediction>(): ColumnType<T> => ({
  title: <StrongTitle label="dataset.column.model" />,
  dataIndex: 'model',
  render: (_, { projectId, inferModel, inferModelId }) => {
    const label = inferModel ? <ModelVersionName result={inferModel} stageId={inferModelId[1]} /> : inferModelId.join(',')
    return <Link to={`/home/project/${projectId}/model/${inferModelId[0]}`}>{label}</Link>
  },
  onCell: ({ rowSpan }) => ({
    rowSpan,
  }),
})

export default Model
