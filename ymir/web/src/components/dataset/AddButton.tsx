import { FC } from 'react'
import { useHistory } from 'umi'
import { Button } from 'antd'

import t from '@/utils/t'
import { AddIcon } from '@/components/common/Icons'

type Props = {
  id?: number | string
}
const AddButton: FC<Props> = ({ id }) => {
  const history = useHistory()
  function add() {
    history.push(`/home/project/${id}/dataset/add`)
  }
  return (
    <Button type="primary" onClick={add}>
      <AddIcon /> {t('dataset.import.label')}
    </Button>
  )
}

export default AddButton
