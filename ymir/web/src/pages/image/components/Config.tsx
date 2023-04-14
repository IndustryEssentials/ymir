import { FC } from 'react'
import { Card, Col, Row } from 'antd'
import { getImageTypeLabel } from '@/constants/image'
import t from '@/utils/t'

const Config: FC<{ configs?: YModels.DockerImageConfig[] }> = ({ configs = [] }) => {
  return (
    <Row gutter={16}>
      {configs.map(({ type, config }) => (
        <Col key={type} span={8}>
          <Card title={t(getImageTypeLabel([type])[0])} bordered={false}>
            {Object.keys(config).map((key) => {
              const value = config[key]
              return (
                <Row key={key}>
                  <Col style={{ width: 200, fontWeight: 'bold' }}>{key}:</Col>
                  <Col>{value}</Col>
                </Row>
              )
            })}
          </Card>
        </Col>
      ))}
    </Row>
  )
}

export default Config
