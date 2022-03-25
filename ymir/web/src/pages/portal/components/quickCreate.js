import { Card } from "antd"
import { Link } from 'umi'
import styles from '../index.less'
const QuickCreate = ({ icon='', link='', label='' }) => {
  return <Card className={`${styles.boxItem} ${styles.emptyBoxItem}`} bodyStyle={{ height: '100%', padding: 0 }}>
    <Link className={styles.emptyBoxAction} to={link}>
      {icon}<span style={{ color: '#36cbcb', fontSize: 16, marginLeft: 10 }}>{label}</span>
    </Link>
  </Card>
}
export default QuickCreate
