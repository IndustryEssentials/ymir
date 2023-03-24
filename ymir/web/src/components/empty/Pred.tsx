import { FC } from 'react'
import { Button, Space } from 'antd'
import { useHistory, useParams } from 'umi'
import t from '@/utils/t'
import DefaultEmpty from './default'
import styles from './empty.less'

const Pred: FC = () => {
  const { id } = useParams<{ id?: string }>()
  const history = useHistory()
  return (
    <Space className={styles.empty} direction="vertical">
      <DefaultEmpty description={<h3>{t('pred.empty.label')}</h3>} />
      <Button type='primary' onClick={() => history.push(`/home/project/${id}/inference`)}>{t('common.action.inference')}</Button>
    </Space>
  )
}

export default Pred
