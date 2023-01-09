import t from '@/utils/t'
import { FC } from 'react'

const StrongTitle: FC<{ label?: string }> = ({ label }) => {
  return <div style={{ textAlign: 'center', fontWeight: 'bold' }}>{t(label)}</div>
}

export default StrongTitle
