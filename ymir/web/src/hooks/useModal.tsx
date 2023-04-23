import { FC, PropsWithChildren, ReactElement, useEffect, useMemo, useState } from 'react'
import { Modal, ModalProps } from 'antd'

type ModalConfig = ModalProps & {}

const useModal = <P extends PropsWithChildren<{}> = {}>(ContentComponent: FC<P>, modalProps?: ModalConfig): [FC<P>, (v?: boolean) => void] => {
  const [visible, setVisible] = useState(false)
  const onCancel = () => setVisible(false)
  const show = (v = true) => setVisible(v)

  const AddModal: FC<P> = useMemo(
    () =>
      ({ ...props }): ReactElement<P> => {
        return (
          <Modal destroyOnClose centered bodyStyle={{ padding: 0 }} footer={null} {...modalProps} onCancel={onCancel} visible={visible}>
            <ContentComponent {...props} back={() => onCancel()} />
          </Modal>
        )
      },
    [visible],
  )

  return [AddModal, show]
}

export default useModal
