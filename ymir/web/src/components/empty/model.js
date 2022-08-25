
import { Button, Space } from 'antd'
import { useHistory, useParams } from 'umi'

import t from '@/utils/t'
import styles from './empty.less'
import { NoXlmxIcon, TrainIcon, ImportIcon } from '@/components/common/icons'

export default ({ style = {} }) => {
  const { id } = useParams()
  const history = useHistory()
  return (
    <Space className={styles.empty} style={style} direction="vertical">
      <NoXlmxIcon className={styles.primaryIcon} style={{ fontSize: 80 }} />
      <h3>{t("model.empty.label")}</h3>
      <Space>
        <Button type="primary" style={{ pointerEvents: 'auto' }} onClick={() => history.push(`/home/project/${id}/train`)}>
          <TrainIcon /> {t('common.action.train')}
        </Button>
        <Button type="primary" style={{ pointerEvents: 'auto' }} onClick={() => history.push(`/home/project/${id}/model/import`)}>
          <ImportIcon /> {t('model.empty.btn.label')}
        </Button>
      </Space>
    </Space>
  )
}
