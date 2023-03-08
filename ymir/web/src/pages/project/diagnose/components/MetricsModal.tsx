import { Modal, ModalProps } from "antd"
import { FC } from "react"
import Metrics from './Metrics'
type Props = ModalProps & {
  project: YModels.Project
}

const MetricsModal: FC<Props> = ({ project, ...props }) => {
  return <Modal {...props}>
    <Metrics project={project}  />
  </Modal>
}

export default MetricsModal
