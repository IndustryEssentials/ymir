import { Row, Col } from "antd"
import { Link } from "umi"
import styles from '../index.less'
import { MoreIcon } from "@/components/common/icons"
const renderTitle = (title, link = '', label = 'More') => <Row>
  <Col flex={1}>{title}</Col>
  { link ? <Col><Link to={link}><MoreIcon title={label} className={styles.moreIcon} /></Link></Col> : null }
  </Row>
export default renderTitle