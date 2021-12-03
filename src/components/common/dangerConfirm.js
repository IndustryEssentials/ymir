import { Modal } from "antd"
import { TipsIcon } from "./icons"

const { confirm } = Modal

const Confirm = (props) => {
  const color = 'rgb(242, 99, 123)'
  confirm({
    icon: <TipsIcon style={{ color }} />,
    okButtonProps: { style: { backgroundColor: color, borderColor: color, } },
    ...props,
  })
}

export default Confirm
