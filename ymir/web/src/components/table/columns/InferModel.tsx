import { ColumnType } from 'antd/lib/table'

import StrongTitle from './StrongTitle'
import ModelVersionName from '@/components/result/ModelVersionName'
import { Link } from 'umi'
import usePrimaryMetric from '@/hooks/usePrimaryMetric'
import { getRecommendStage } from '@/constants/model'

const Model = <T extends YModels.Prediction>(): ColumnType<T> => ({
  title: <StrongTitle label="dataset.column.model" />,
  dataIndex: 'model',
  render: (_, { type, projectId, inferModel, inferModelId }) => {
    const Metric = usePrimaryMetric(({ metricLabel, metric, percent }) => {
      return (
        <>
          {metricLabel}: {percent}
        </>
      )
    })
    const stage = inferModel ? getRecommendStage(inferModel) : undefined
    const label = inferModel ? <ModelVersionName result={inferModel} stageId={inferModelId[1]} /> : inferModelId.join(',')
    return (
      <Link to={`/home/project/${projectId}/model/${inferModelId[0]}`}>
        <span>{label}</span> <br />
        <Metric type={type} primaryMetric={stage?.primaryMetric} />
      </Link>
    )
  },
  onCell: ({ rowSpan }) => ({
    rowSpan,
  }),
})

export default Model
