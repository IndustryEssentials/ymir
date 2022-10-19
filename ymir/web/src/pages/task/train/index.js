import { Card } from "antd"
import { useLocation } from "umi"

import t from "@/utils/t"

import Breadcrumbs from "@/components/common/breadcrumb"
import Training from "@/components/task/training"

import commonStyles from "../common.less"

function TrainPage() {
  const { query } = useLocation()

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.training')}>
        <Training query={query} />
      </Card>
    </div>
  )
}

export default TrainPage
