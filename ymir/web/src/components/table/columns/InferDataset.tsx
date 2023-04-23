import { ColumnType } from 'antd/lib/table'

import StrongTitle from './StrongTitle'
import VersionName from '@/components/result/VersionName'
import { Link } from 'umi'
import { Prediction } from '@/constants'

const InferDataset = <T extends Prediction>(): ColumnType<T> => ({
  title: <StrongTitle label="dataset.type.testing" />,
  dataIndex: 'inferDatasetId',
  render: (_, { projectId, inferDatasetId, inferDataset }) => {
    const label = inferDataset ? <VersionName result={inferDataset} /> : inferDatasetId
    return <Link to={`/home/project/${projectId}/dataset/${inferDatasetId}`}>{label}</Link>
  },
})

export default InferDataset
