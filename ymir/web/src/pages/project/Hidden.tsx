import { useEffect, useState } from "react"
import s from "./index.less"
import { useLocation, useParams } from "umi"

import { tabs } from '@/constants/project'
import Breadcrumbs from "@/components/common/breadcrumb"
import HiddenList from "./components/HiddenList"

function Hidden() {
  const location = useLocation()
  const { id } = useParams<{ id: string }>()
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
