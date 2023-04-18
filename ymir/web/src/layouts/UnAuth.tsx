import { FC, useEffect } from 'react'
import { useHistory, useSelector } from 'umi'
import { Layout } from 'antd'

import Loading from '@/components/common/Loading'

import styles from './common.less'

const { Content } = Layout

const UnAuthLayout: FC = ({ children }) => {
  const history = useHistory()
  const logined = useSelector(({ user }) => user.logined)

  useEffect(() => {
    if (logined) {
      history.replace('/home/portal')
    }
  }, [])
  return (
    <>
      <Layout className={styles.unauth}>
        <Content className={styles.content}>{children}</Content>
      </Layout>
      <Loading />
    </>
  )
}

export default UnAuthLayout
