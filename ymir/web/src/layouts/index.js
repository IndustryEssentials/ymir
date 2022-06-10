import commonStyles from "./common.less"
import { connect } from "dva"
import HeaderNav from "@/components/nav/index"
import React, { useEffect } from "react"
import { ConfigProvider, Layout, message } from "antd"
import Loading from "@/components/common/loading"
import Foot from "@/components/common/footer"
import LeftMenu from "@/components/common/leftMenu"
import Empty from '@/components/empty/default'
import '@/assets/icons/iconfont.css'
import { withRouter } from "umi"

const { Header, Content, Sider, Footer } = Layout
message.config({ maxCount: 1 })

function BasicLayout(props) {
  let { logined, history } = props
  useEffect(() => {
    if (!logined) {
      history.replace(`/login?redirect=${history.location.pathname}`)
      return
    }
    props.getUserInfo()
  }, [logined])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [history.location.pathname])

  return (
    <ConfigProvider renderEmpty={() => <Empty />}>
      <Layout className={commonStyles.home}>
        <Header>
          <HeaderNav></HeaderNav>
        </Header>
        <Layout>
          <LeftMenu></LeftMenu>
          <Layout>
            <Content
              className={commonStyles.content}
              style={{
                minHeight: document.documentElement.clientHeight - 60 - 50,
              }}
            >
              {props.children}
            </Content>
            <Footer className={commonStyles.footer}>
              <Foot></Foot>
            </Footer>
          </Layout>
        </Layout>
      </Layout>
      <Loading />
      {/* <QuickActions />
      <Guide /> */}
    </ConfigProvider>
  )
}

const mapStateToProps = (state) => {
  return {
    logined: state.user.logined,
  }
}
const mapDispatchToProps = (dispatch) => {
  return {
    getUserInfo: () => {
      return dispatch({
        type: "user/getUserInfo",
      })
    },
  }
}
export default withRouter(connect(mapStateToProps, mapDispatchToProps)(BasicLayout))
