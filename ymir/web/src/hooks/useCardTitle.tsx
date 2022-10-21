import { Button, Col, Row } from "antd"
import t from '@/utils/t'
import { useHistory } from "umi"

export default function useCardTitle(label = '') {
  const history = useHistory()
  return (
    <Row>
      <Col flex={1}>{t(label)}</Col>
      <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
    </Row>
  )
}