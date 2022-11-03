import { FailIcon, TipsIcon } from "@/components/common/Icons"
import s from './tip.less'

const Tip = ({ type = 'success', content = '' }) => {
  return content ? (
    <div className={`${s.tipContainer} ${s[type]}`}>
      {getIcon(type)}
      {content}
    </div>
  ) : null
}

function getIcon(type) {
  const cls = `${s.icon} ${s[type]}`
  return type === 'success' ? <TipsIcon className={cls} /> : <FailIcon className={cls} />
}

export default Tip
