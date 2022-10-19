import { Card, } from "antd"
import { useLocation } from "umi"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"

import commonStyles from "../common.less"
import Label from "@/components/task/label"

function LabelPage() {
  const { query } = useLocation()

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.label')}>
        <Label query={{ ...query }} />
      </Card>
    </div>
  )
}

export default LabelPage
