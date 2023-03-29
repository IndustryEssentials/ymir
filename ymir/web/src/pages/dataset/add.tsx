import { FC } from 'react'
import { useLocation, Location } from 'umi'

import Add from '@/components/dataset/Add'
import Breadcrumbs from '@/components/common/breadcrumb'

const AddPage: FC = () => {
  const location: Location = useLocation()
  const { id, from, stepKey } = location.query as { id?: string; from?: string; stepKey?: string }
  return (
    <div className={'datasetImport'} style={{ height: '100%' }}>
      <Breadcrumbs />
      <Add id={Number(id)} from={from} stepKey={stepKey} style={{ height: 'calc(100vh - 186px)'}} />
    </div>
  )
}

export default AddPage
