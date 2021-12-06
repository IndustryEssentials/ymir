import { Col, Row } from "antd"
import styles from "./index.less"
import LangBtn from "@/components/common/langBtn"

const Header = () => {
  return (
    <Row className={styles.headerbar}>
      <Col span={24}>
        <LangBtn />
      </Col>
    </Row>
  )
}

export default Header
