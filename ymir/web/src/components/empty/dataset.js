
import { Button, Space } from 'antd'

import t from '@/utils/t'
import styles from './empty.less'
import { NoSjjIcon, ImportIcon, } from '@/components/common/icons'

export default ({ style = {}, add = () => {} }) => (
  <Space className={styles.empty} style={style} direction="vertical">
    <NoSjjIcon className={styles.primaryIcon} style={{ fontSize: 80 }} />
    <h3>{t("dataset.empty.label")}</h3>
    <Button type="primary" onClick={add}>
      <ImportIcon /> {t("dataset.import.label")}
    </Button>
  </Space>
)