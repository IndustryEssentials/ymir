import { Card } from "antd"
import { Link } from 'umi'
import styles from '../index.less'
const QuickAction = ({ icon='', link='', label='' }) => {
  
  return <Card className={`${styles.boxItem} ${styles.emptyBoxItem}`} bodyStyle={{ height: '100%', padding: 0 }}>
  <Link className={styles.emptyBoxAction} to={link}>
    {icon}<br /><span style={{ color: '#000000D9', fontSize: 16 }}>{label}</span>
  </Link>
</Card>
}
export default QuickAction
