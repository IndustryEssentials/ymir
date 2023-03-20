import { Spin } from "antd"
import { useSelector } from 'umi'
import styles from "./common.less"

function Loading() {
  const globalLoading = useSelector(({ loading }) => loading.global && !loading.models.Verify)
  const commonLoading = useSelector(({ common }) => common.loading)
  return (
    <div className={styles.loading} style={{ display: globalLoading && commonLoading ? "" : "none" }}>
      <Spin size="large" />
    </div>
  )
}

export default Loading
