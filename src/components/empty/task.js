
import { Button, Space } from 'antd'
import { useHistory } from 'umi'

import t from '@/utils/t'
import styles from './empty.less'
import { NavTaskIcon, AddIcon } from '@/components/common/icons'

export default ({ style = {}}) => {
  const history = useHistory()
  return (
    <Space className={styles.empty} style={style} direction="vertical">
      <NavTaskIcon className={styles.primaryIcon} style={{ fontSize: 80 }} />
      <h3>{t("task.empty.label")}</h3>
      <Button type="primary" onClick={() => history.push('/home/task')}>
        <AddIcon /> {t('task.add.label')}
      </Button>
    </Space>
  )
}
