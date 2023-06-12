import React, { FC, useEffect } from 'react'
import { ConfigProvider, Layout, message } from 'antd'
import { useHistory, withRouter, useSelector } from 'umi'

import useRequest from '@/hooks/useRequest'

import Loading from '@/components/common/Loading'
import Empty from '@/components/empty/Default'
import LeftMenu from '@/components/common/LeftMenu'
import HeaderNav from '@/components/common/Nav'
import Foot from '@/components/common/Footer'

import commonStyles from './common.less'
import '@/assets/icons/iconfont.css'
import Notification from '@/components/message/Notification'
import OfficialImageTip from '@/components/image/OfficialImageTip'

const { Header, Content, Sider, Footer } = Layout
message.config({ maxCount: 1 })

const BasicLayout: FC = ({ children }) => {
  const history = useHistory()
  const logined = useSelector(({ user }) => user.logined)
  const { run: getUserInfo } = useRequest('user/getUserInfo')

  useEffect(() => {
    if (!logined) {
      window.location.href = `/login?redirect=${history.location.pathname}`
      return
    }
    getUserInfo()
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
          <Layout className="layoutContent">
            <Content
              className={commonStyles.content}
              style={{
                minHeight: document.documentElement.clientHeight - 60 - 50,
              }}
            >
              {children}
            </Content>
            <Footer className={commonStyles.footer}>
              <Foot></Foot>
            </Footer>
          </Layout>
        </Layout>
      </Layout>
      <Loading />
      <Notification />
      <OfficialImageTip />
    </ConfigProvider>
  )
}
export default withRouter(BasicLayout)
