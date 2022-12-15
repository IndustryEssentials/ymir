import { Button, Col, Row } from "antd"
import t from '@/utils/t'
import { useHistory } from "umi"

export default function useCardTitle(label = '', name: string) {
  const history = useHistory()
  return (
    <Row>
      <Col flex={1}>{name ? name : t(label)}</Col>
      <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
    </Row>
  )
}