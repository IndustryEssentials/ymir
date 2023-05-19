import { FC } from 'react'
import { useLocation, Location } from 'umi'

import Breadcrumbs from '@/components/common/breadcrumb'
import BatchAdd from '@/components/dataset/BatchAdd'

const AddPage: FC = () => {
  const location: Location = useLocation()
  const { id, from, stepKey } = location.query as { id?: string; from?: string; stepKey?: string }
  return (
    <div className={'datasetImport'} style={{ height: '100%' }}>
      <Breadcrumbs />
      <BatchAdd />
    </div>
  )
}

export default AddPage
