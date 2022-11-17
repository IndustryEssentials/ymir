import { TipsIcon } from './Icons'

const color = 'rgb(242, 99, 123)'
const confirmConfig = (props) => ({
  icon: <TipsIcon style={{ color }} />,
  okButtonProps: { style: { backgroundColor: color, borderColor: color } },
  ...props,
})

export default confirmConfig
