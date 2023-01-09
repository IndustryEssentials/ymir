import { ColumnType } from 'antd/lib/table'
import { Col, Row } from 'antd'

import { getRecommendStage, validModel } from '@/constants/model'
import { percent } from '@/utils/number'
import StrongTitle from './StrongTitle'

const Stages = <T extends YModels.Model>(): ColumnType<T> => ({
  title: <StrongTitle label="model.column.stage" />,
  dataIndex: 'recommendStage',
  render: (_, record) => {
    const stage = getRecommendStage(record)
    return validModel(record) ? (
      <Row wrap={false}>
        <Col flex={1}>{stage?.name}</Col>
        <Col style={{ color: 'orange' }}>mAP: {percent(stage?.map || 0)}</Col>
      </Row>
    ) : null
  },
  width: 300,
})

export default Stages
