import { useEffect, useState } from "react"
import s from "./index.less"
import { useLocation, useParams } from "umi"

import Breadcrumbs from "@/components/common/breadcrumb"
import HiddenList, { AType } from "./components/HiddenList"

function Hidden() {
  const location = useLocation()
  const { id } = useParams<{ id: string }>()
  const [active, setActive] = useState<AType>()

  useEffect(() => {
    const tabKey = location.hash.replace(/^#/, '') as AType
    setActive(tabKey || 'dataset')
  }, [location.hash])

  return (
    <div className={s.hiddenList}>
      <Breadcrumbs />
      <HiddenList active={active} pid={id} />
    </div>
  )
}

export default Hidden
