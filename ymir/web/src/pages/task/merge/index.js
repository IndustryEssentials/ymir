import React, {  } from "react"
import { Form, Card } from "antd"
import { useLocation } from "umi"

import t from "@/utils/t"

import Breadcrumbs from "@/components/common/breadcrumb"

import commonStyles from "../common.less"
import Merge from "@/components/task/merge"

function MergePage() {
  const { query } = useLocation()

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('task.fusion.header.merge')}>
        <Merge query={query} />
      </Card>
    </div>
  )
}

export default MergePage
