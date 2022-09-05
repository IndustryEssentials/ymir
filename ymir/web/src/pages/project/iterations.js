import React, {  } from "react"
import { Card, } from "antd"

import Breadcrumbs from "@/components/common/breadcrumb"

import s from "./index.less"

function Iterations() {

  return (
    <div className={s.iterations}>
      <Breadcrumbs />
      <div className={s.header}>
        processing
      </div>
      <Card tabList={[{}, {}]}>
        detail | history list
      </Card>
    </div>
  )
}


export default Iterations
