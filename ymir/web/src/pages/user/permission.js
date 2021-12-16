import { Card } from "antd"
import { connect } from "dva"
import { Link, useHistory, useParams } from "umi"
import { useState } from "react"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import UserList from "./permission/UserList"
import AuditList from "./permission/AuditList"
import s from './permission.less'

const tabsTitle = [
  { tab: t('permission.tabs.permission'), key: 'permission', },
  { tab: t('permission.tabs.audit'), key: 'audit', },
]

const Permission = () => {
  const [active, setActive] = useState(tabsTitle[0].key)

  const contents = {
    [tabsTitle[0].key]: <UserList />,
    [tabsTitle[1].key]: <AuditList />,
  }
  return (
    <div className={s.permission}>
      <Breadcrumbs />
      <Card tabList={tabsTitle} activeTabKey={active} onTabChange={(key) => setActive(key)}>
        {contents[active]}
      </Card>
    </div>
  )
}

const props = (state) => {
  return {

  }
}
const actions = (dispatch) => {
  return {}
}
export default connect(props, actions)(Permission)