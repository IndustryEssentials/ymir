import { useLocation } from "umi"


import Breadcrumbs from "@/components/common/breadcrumb"
import Fusion from "@/components/task/fusion"
import useSubmitHandle from "../components/useSubmitHandle"

function FusionIndex() {
  const { query } = useLocation()
  const submitHandle = useSubmitHandle()
  return (
    <div>
      <Breadcrumbs />
      <Card title={t('breadcrumbs.task.fusion')}>
        <Fusion query={query} ok={submitHandle} />
      </Card>
    </div>
  )
}

export default FusionIndex
