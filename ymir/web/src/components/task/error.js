import { useState } from 'react'
import t from '@/utils/t'
import { Descriptions } from 'antd'
import {
  ArrowDownIcon, ArrowUpIcon,
} from "@/components/common/Icons"
import s from './detail.less'

const { Item } = Descriptions
const labelStyle = {
  width: "15%",
  paddingRight: "20px",
  justifyContent: "flex-end",
}

export default function Error({ code, msg = '', terminated }) {
  const [visible, setVisible] = useState(false)

  function formatErrorMessage(message) {
    return <div hidden={!visible}>
      {message.split('\n').map((item, i) => <div key={i}>{item}</div>)}
    </div>
  }

  const renderError = <>
    <Item label={t("task.detail.error.code")}>
      {code ? t(`error${code}`) : null}
      {msg ? <span className='more' onClick={() => setVisible(!visible)}>{visible ? <ArrowUpIcon /> : <ArrowDownIcon />}</span> : null}
    </Item>
    {msg && visible ? <Item label={t('task.detail.error.desc')} style={{ lineHeight: 1.25 }}>
      {formatErrorMessage(msg)}
    </Item> : null}
  </>

  const renderTerminated = <Item label={t("task.detail.terminated.label")}>
    {t('task.detail.terminated')}
  </Item>

  return terminated || code ? <div className='error'>
    <Descriptions
      bordered
      column={1}
      labelStyle={labelStyle}
      title={<div className='title'>{t("task.state")}</div>}
      className='infoTable'
    >
      {terminated ? renderTerminated : renderError }
    </Descriptions>
  </div> : null
}