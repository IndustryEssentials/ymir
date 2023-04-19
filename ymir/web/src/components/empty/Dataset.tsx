
import { Button, Space } from 'antd'

import { useHistory, useParams } from 'umi'
import t from '@/utils/t'

import AddButton from '@/components/dataset/AddButton'

import styles from './empty.less'
import { NoSjjIcon, ImportIcon, } from '@/components/common/Icons'

export default ({ style = {} }) => {
  const { id } = useParams<{ id?: string }>()
  return (
    <Space className={styles.empty} style={style} direction="vertical">
      <NoSjjIcon className={styles.primaryIcon} style={{ fontSize: 80 }} />
      <h3>{t("dataset.empty.label")}</h3>
      <AddButton />
    </Space>
  )
}
