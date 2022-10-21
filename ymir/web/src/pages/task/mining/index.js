import React, { } from "react"
import { useLocation } from "umi"
import { Card } from "antd"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import Mining from "@/components/task/mining"

import commonStyles from "../common.less"
import useSubmitHandle from "../components/useSubmitHandle"

function MiningPage() {
  const { query } = useLocation()
  const submitHandle = useSubmitHandle()
  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.mining')}>
        <Mining query={query} ok={submitHandle} />
      </Card>
    </div>
  )
}

export default MiningPage
