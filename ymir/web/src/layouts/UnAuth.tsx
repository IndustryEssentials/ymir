import styles from "./common.less"
import { Layout } from "antd"
import { connect } from 'dva'
import { useHistory } from "umi"
import Loading from "@/components/common/loading"
import { useEffect } from "react"

const { Header, Content } = Layout

function UnAuthLayout(props) {
  const history = useHistory()
  useEffect(() => {
    if (props.logined) {
      history.replace('/home/portal')
    }
  }, [])
  return (
    <>
    <Layout className={styles.unauth}>
      <Content className={styles.content}>{props.children}</Content>
    </Layout>
    <Loading />
    </>
  )
}

const actions = (state) => {
  return {
    logined: state.user.logined,
  }
}

export default connect(actions)(UnAuthLayout)
