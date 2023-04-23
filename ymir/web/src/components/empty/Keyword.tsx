import { CSSProperties, FC } from 'react'
import { Button, Space } from 'antd'
import { useHistory } from 'umi'

import t from '@/utils/t'
import styles from './empty.less'
import { NoXlmxIcon } from '@/components/common/Icons'
import { AddtaskIcon } from '../common/Icons'

const Keyword: FC<{ style?: CSSProperties }> = ({ style }) => {
  const history = useHistory()
  return (
    <Space className={styles.empty} style={style} direction="vertical">
      <NoXlmxIcon className={styles.primaryIcon} style={{ fontSize: 80 }} />
      <h3>{t('keyword.empty.label')}</h3>
      <Button type="primary" onClick={() => history.replace({ pathname: '/home/keyword', state: { type: 'add' } })}>
        <AddtaskIcon /> {t('keyword.empty.btn.label')}
      </Button>
    </Space>
  )
}

export default Keyword
