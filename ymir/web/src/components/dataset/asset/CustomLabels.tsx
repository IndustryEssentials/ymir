import { Col, Row, Space } from 'antd'
import { FC } from 'react'
type Props = { asset?: YModels.Asset }

const CustomLabels: FC<Props> = ({ asset }) => {
  const cks = asset?.cks || {}
  return (
    <>
      {cks
        ? Object.keys(cks).map((ck) => (
            <Row key={ck}>
              <Col><span style={{ fontWeight: 'bold' }}>{ck}: </span> <span>{cks[ck]}</span></Col>
            </Row>
          ))
        : null}
    </>
  )
}

export default CustomLabels
