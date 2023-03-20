import { FC, useState } from 'react'
import t from '@/utils/t'
import { Descriptions } from 'antd'
import { ArrowDownIcon, ArrowUpIcon } from '@/components/common/Icons'
import s from './detail.less'
import { getErrorCodeDocLink } from '@/constants/common'

const { Item } = Descriptions
const labelStyle = {
  width: '15%',
  paddingRight: '20px',
  justifyContent: 'flex-end',
}

const ErrorMessage: FC<{ code: string; msg?: string; terminated?: boolean }> = ({ code, msg = '', terminated }) => {
  const [visible, setVisible] = useState(false)

  function formatErrorMessage(message: string) {
    return (
      <div hidden={!visible}>
        {message.split('\n').map((item, i) => (
          <div key={i}>{item}</div>
        ))}
      </div>
    )
  }

  const renderError = (
    <>
      <Item label={t('task.detail.error.code')}>
        {code ? <span>{t(`error${code}`)}</span> : null}
        <a className={s.more} href={getErrorCodeDocLink(code)} target="_blank">
          {t('common.more')}
        </a>
      </Item>
      {msg && visible ? (
        <Item label={t('task.detail.error.desc')} style={{ lineHeight: 1.25 }}>
          {formatErrorMessage(msg)}
        </Item>
      ) : null}
    </>
  )

  const renderTerminated = <Item label={t('task.detail.terminated.label')}>{t('task.detail.terminated')}</Item>

  return terminated || code ? (
    <div className="error">
      <Descriptions bordered column={1} labelStyle={labelStyle} title={<div className="title">{t('task.state')}</div>} className="infoTable">
        {terminated ? renderTerminated : renderError}
      </Descriptions>
    </div>
  ) : null
}

export default ErrorMessage
