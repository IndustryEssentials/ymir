
import { Col, Row, Tag } from "antd"

import AddKeywordsBtn from "../keyword/addKeywordsBtn"

function IgnoreKeywords({ keywords = [] }) {
  return (
    <Row wrap={false}>
      <Col flex={1}>
        {keywords.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Col>
      <Col>
        {keywords.length ? <AddKeywordsBtn type="primary" keywords={keywords} /> : null }
      </Col>
    </Row>
  )
}

export default IgnoreKeywords
