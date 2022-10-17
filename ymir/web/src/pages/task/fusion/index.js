import { useLocation } from "umi"


import Breadcrumbs from "@/components/common/breadcrumb"
import Fusion from "@/components/task/fusion"

function FusionIndex() {
  const { query } = useLocation()
  const { merging } = query
  const did = Number(query.did)
  return (
    <div>
      <Breadcrumbs />
      <Card title={t('breadcrumbs.task.fusion')}>
        <Fusion did={did} merging={merging} />
      </Card>
    </div>
  )
}

export default FusionIndex
