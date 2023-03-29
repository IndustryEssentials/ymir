import { Modal, ModalProps } from 'antd'
import { FC } from 'react'
import Add from './Add'
type Props = ModalProps & {}

const AddModal: FC<Props> = ({ ...props }) => {
  return (
    <Modal width={'96%'} centered bodyStyle={{ padding: 0 }} {...props} footer={null}>
      <Add back={(e) => {props.onCancel && props.onCancel(e)}} />
    </Modal>
  )
}

export default AddModal
