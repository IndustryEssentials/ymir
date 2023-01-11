import { TipsIcon } from './Icons'

const color = 'rgb(242, 99, 123)'

const DangerConfirm = (props: { [key: string]: any }) => ({
  icon: <TipsIcon style={{ color }} />,
  okButtonProps: { style: { backgroundColor: color, borderColor: color } },
  ...props,
})

export default DangerConfirm
