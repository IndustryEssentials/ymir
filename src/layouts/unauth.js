import styles from "./common.less"
import HeaderNav from "@/components/header/index"
import { Layout } from "antd"
import Loading from "@/components/common/loading"

const { Header, Content } = Layout

function UnAuthLayout(props) {
  return (
    <>
    <Layout className={styles.unauth}>
      {/* <Header className={styles.header}>
        <HeaderNav></HeaderNav>
      </Header> */}
      <Content className={styles.content}>{props.children}</Content>
    </Layout>
    <Loading />
    </>
  )
}

export default UnAuthLayout
