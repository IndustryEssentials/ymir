import React, { useEffect, useState } from "react"
import s from "./index.less"
import { useHistory, useLocation, useParams } from "umi"
import { Card, } from "antd"

import t from "@/utils/t"
import { tabs } from '@/constants/project'
import Breadcrumbs from "@/components/common/breadcrumb"
import HiddenList from "./components/hiddenList"

function Hidden() {
  const history = useHistory()
  const location = useLocation()
  const { id } = useParams()
  const [active, setActive] = useState(tabs[0].key)

  useEffect(() => {
    const tabKey = location.hash.replace(/^#/, '')
    setActive(tabKey || tabs[0].key)
  }, [location.hash])
  
  function tabChange(key) {
    history.push(`#${key}`)
  }

  return (
    <div className={s.hiddenList}>
      <Breadcrumbs />
      <Card tabList={tabs.map(tab => ({ ...tab, tab: t(tab.tab) }))} activeTabKey={active} onTabChange={tabChange}
        className='noShadow'
        bordered={false}
        style={{ margin: '-20px -5vw 0', background: 'transparent' }}
        headStyle={{ padding: '0 5vw', background: '#fff', marginBottom: '20px' }}
        bodyStyle={{ padding: '0 5vw' }}>
        <HiddenList module={active} pid={id} />
      </Card>
    </div>
  )
}

export default Hidden
