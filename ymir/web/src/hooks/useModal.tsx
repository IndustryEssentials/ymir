import { FC, PropsWithChildren, ReactElement, useState } from 'react'
import { Modal, ModalProps } from 'antd'

type ModalConfig = ModalProps & {}

const useModal = <P extends PropsWithChildren<{}> = {}>(ContentComponent: FC<P>, modalProps?: ModalConfig): [FC<P>, () => void] => {
  const [visible, setVisible] = useState(false)
  const onCancel = () => setVisible(false)
  const show = () => setVisible(true)

  const AddModal: FC<P> = ({ ...props }): ReactElement<P> => {
    return (
      <Modal destroyOnClose centered bodyStyle={{ padding: 0 }} footer={null} {...modalProps} onCancel={onCancel} visible={visible}>
        <ContentComponent {...props} back={() => onCancel()} />
      </Modal>
    )
  }

  return [AddModal, show]
}

export default useModal
