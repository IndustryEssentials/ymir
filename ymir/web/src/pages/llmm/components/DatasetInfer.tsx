import { FC, useState, useEffect } from 'react'
import { useSelector } from 'umi'
import t from '@/utils/t'
import { Dataset } from '@/constants'
type Props = {}
const DatasetInfer: FC<Props> = ({}) => {
  const [dataset, setDataset] = useState<Dataset>()

  useEffect(() => {}, [])
  return <></>
}
export default DatasetInfer
