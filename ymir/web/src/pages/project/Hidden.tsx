import React, { useEffect, useState } from "react"
import s from "./index.less"
import { useHistory, useLocation, useParams } from "umi"

import t from "@/utils/t"
import { tabs } from '@/constants/project'
import Breadcrumbs from "@/components/common/breadcrumb"
import HiddenList from "./components/hiddenList"

function Hidden() {
  const location = useLocation()
  const { id } = useParams()
  const [active, setActive] = useState(tabs[0].key)

  useEffect(() => {
    const tabKey = location.hash.replace(/^#/, '')
    setActive(tabKey || tabs[0].key)
  }, [location.hash])

  return (
    <div className={s.hiddenList}>
      <Breadcrumbs />
      <HiddenList module={active} pid={id} />
    </div>
  )
}

export default Hidden
