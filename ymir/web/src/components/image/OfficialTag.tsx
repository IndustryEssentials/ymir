import t from '@/utils/t'
import React from 'react'

const OfficialTag: React.FC<{ official?: boolean }> = ({ official }) => {
  return official ? <span className='extraTag' style={{ background: '#3ab53a'}}>{t('image.official.label')}</span> : null
}

export default OfficialTag
