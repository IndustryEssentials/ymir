import { useState } from 'react'
import t from '@/utils/t'
import { Descriptions } from 'antd'
import {
  ArrowDownIcon, ArrowUpIcon,
} from "@/components/common/icons"
import s from './detail.less'

const { Item } = Descriptions
const labelStyle = {
  width: "15%",
  paddingRight: "20px",
  justifyContent: "flex-end",
}

export default function Error({ code, msg = '' }) {
  const [visible, setVisible] = useState(false)

  function formatErrorMessage(message) {
    return <div hidden={!visible}>
      {message.split('\n').map((item, i) => <div key={i}>{item}</div>)}
    </div>
  }

  return <div className='error'>

    <Descriptions
      bordered
      column={1}
      labelStyle={labelStyle}
      title={<div className='title'>{t("task.detail.error.title")}</div>}
      className='infoTable'
    >
      <Item label={t("task.detail.error.code")}>
        {t(`error${code}`)} 
        {msg ? <span className='more' onClick={() => setVisible(!visible)}>{visible ? <ArrowUpIcon /> : <ArrowDownIcon />}</span> : null}
      </Item>
      {msg && visible ? <Item label={t('task.detail.error.desc')} style={{ lineHeight: 1.25 }}>
        {formatErrorMessage(msg)}
      </Item> : null}
    </Descriptions>
  </div>
}