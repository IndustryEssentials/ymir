import { FC } from 'react'
import { useHistory, useParams } from 'umi'
import { Button, ButtonProps } from 'antd'

import t from '@/utils/t'
import { AddIcon } from '@/components/common/Icons'

const AddButton: FC<ButtonProps> = ({ ...props }) => {
  const history = useHistory()
  const { id } = useParams<{ id: string}>()
  function add() {
    history.push(`/home/project/${id}/dataset/add`)
  }
  return (
    <Button type="primary" {...props} onClick={add}>
      <AddIcon /> {t('dataset.import.label')}
    </Button>
  )
}

export default AddButton
