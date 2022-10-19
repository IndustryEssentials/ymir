import { Card, } from "antd"
import { useLocation } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"

import commonStyles from "../common.less"
import Label from "@/components/task/label"
import useSubmitHandle from "../components/useSubmitHandle"

function LabelPage() {
  const { query } = useLocation()
  const submitHandle = useSubmitHandle()

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.label')}>
        <Label query={query} ok={submitHandle} />
      </Card>
    </div>
  )
}

export default LabelPage
