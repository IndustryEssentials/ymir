
import { Button, Space } from 'antd'
import { useHistory } from 'umi'

import t from '@/utils/t'
import styles from './empty.less'
import { NoXlmxIcon, TrainIcon, } from '@/components/common/icons'

export default ({ id, style={} }) => {
  const history = useHistory()
  return (
    <Space className={styles.empty} style={style} direction="vertical">
      <NoXlmxIcon className={styles.primaryIcon} style={{ fontSize: 80 }} />
      <h3>{t("model.empty.label")}</h3>
      <Button type="primary" style={{ pointerEvents: 'auto' }} onClick={() => history.push(`/home/project/${id}/model/import`)}>
        <TrainIcon /> {t('model.empty.btn.label')}
      </Button>
    </Space>
  )
}
