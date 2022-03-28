import { Col, Row } from "antd"
import { ArrowDownIcon, ArrowRightIcon } from '@/components/common/icons'
import s from './panel.less'

const Panel = ({ hasHeader = true, visible = false, setVisible = () => {}, label = '', children }) => {

  return (
    <div className={s.panel}>
      {hasHeader ? <Row className={s.header} onClick={() => setVisible(!visible)}>
        <Col flex={1} className={s.title}>{label}</Col>
        <Col className={s.foldBtn}>{visible ? <span><ArrowDownIcon /></span> : <span><ArrowRightIcon /></span>}</Col>
      </Row> : null}
      <div className={s.content} hidden={hasHeader ? !visible : false}>
        {children}
      </div>
    </div>
  )
}

export default Panel
