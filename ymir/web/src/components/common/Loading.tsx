import { Spin } from 'antd'
import { useSelector } from 'react-redux'
import styles from './common.less'

const Loading = () => {
  const globalLoading = useSelector<YStates.Root, boolean>(({ loading }) => loading.global && !loading.models.Verify)
  const commonLoading = useSelector<YStates.Root, boolean>(({ common }) => common.loading)
  return (
    <div className={styles.loading} style={{ display: globalLoading && commonLoading ? '' : 'none' }}>
      <Spin size="large" />
    </div>
  )
}

export default Loading
