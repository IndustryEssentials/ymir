import { Card } from "antd"
import { useLocation } from "umi"

import t from "@/utils/t"

import Breadcrumbs from "@/components/common/breadcrumb"
import Training from "@/components/task/training"

import commonStyles from "../common.less"
import useSubmitHandle from "../components/useSubmitHandle"

function TrainPage() {
  const { query } = useLocation()
  const submitHandle = useSubmitHandle('model')

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.training')}>
        <Training query={query} ok={submitHandle} />
      </Card>
    </div>
  )
}

export default TrainPage
