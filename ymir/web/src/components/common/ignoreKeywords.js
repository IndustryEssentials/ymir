
import { connect } from "dva"
import { Button, Col, message, Row, Tag } from "antd"

import t from "@/utils/t"

function IgnoreKeywords({ keywords = [], addKeywords }) {
  async function addIgnoreKeywords() {
    if (!keywords.length) {
      return
    }
    const params = keywords.map(k => ({
      name: k, alias: []
    }))
    const result = await addKeywords(params)
    if (result) {
      message.success(t('keyword.add.success'))
    }
  }
  return (
    <Row wrap={false}>
      <Col flex={1}>
        {keywords.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Col>
      <Col>
        {keywords.length ? <Button type="primary" onClick={() => addIgnoreKeywords()}>{t("dataset.add.label_strategy.add")}</Button> : null }
      </Col>
    </Row>
  )
}
const actions = (dispatch) => {
  return {
    addKeywords(keywords) {
      return dispatch({
        type: "keyword/updateKeywords",
        payload: { keywords },
      })
    },
  }
}
export default connect(null, actions)(IgnoreKeywords)
