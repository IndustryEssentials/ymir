import { Row, Col } from "antd"
import { Link } from "umi"
import styles from '../index.less'
import { MoreIcon } from "@/components/common/icons"

const BoxTitle = ({ title, link = '', label = 'More', children }) => <Row>
  <Col flex={1}>{title}</Col>
  <Col>{children}</Col>
  { link ? <Col><Link className='more' to={link}><MoreIcon title={label} className={styles.moreIcon} /></Link></Col> : null }
  </Row>
export default BoxTitle