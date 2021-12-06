import { Spin } from "antd"
import { connect } from "dva"
import styles from "./common.less"

function Loading({ loading }) {
  return (
    <div className={styles.loading} style={{ display: loading ? "" : "none" }}>
      <Spin size="large" />
    </div>
  )
}

const mapStateToProps = (state) => {
  return {
    loading: state.loading.global && !state.loading.models.Verify,
  }
}

export default connect(mapStateToProps, null)(Loading)
