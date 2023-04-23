import Breadcrumbs from '@/components/common/breadcrumb'
import Analysis from '@/components/dataset/Analysis'

import style from './analysis.less'
const AnalysisPage = () => {
  return (
    <div className={style.wrapper}>
      <Breadcrumbs />
      <Analysis ids={[9, 10]} type={2} />
    </div>
  )
}

export default AnalysisPage
