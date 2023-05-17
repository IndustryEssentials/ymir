import { Modal, ModalProps } from "antd"
import { FC } from "react"
import Metrics from './Metrics'
type Props = ModalProps & {
  prediction?: YModels.Prediction
}

const MetricsModal: FC<Props> = ({ prediction, ...props }) => {
  return prediction ? <Modal width={'90%'} bodyStyle={{ height: '100%'}} centered {...props} destroyOnClose>
    <Metrics prediction={prediction}  />
  </Modal> : null
}

export default MetricsModal
