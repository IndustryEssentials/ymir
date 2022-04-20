import t from '@/utils/t'
import { Descriptions } from 'antd'
import { useState } from 'react'
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
    return <div hidden={!visible} style={{ padding: 20 }}>
      {message.split('\n').map((item, i) => <div key={i}>{item}</div>)}
    </div>
  }

  return <div className={s.error}>

    <Descriptions
      bordered
      column={1}
      labelStyle={labelStyle}
      title={<div className={s.title}>{t("task.detail.error.title")}</div>}
      className={s.infoTable}
    >
      <Item label={t("task.detail.error.code")}>{t(`error${code}`)}{msg ? <span className='more' onClick={() => setVisible(!visible)}>More</span> : null}</Item>
      {msg && visible ? <Item label={t('task.detail.error.desc')} style={{ lineHeight: 1.25 }}>
        {formatErrorMessage(msg)}
      </Item> : null}
    </Descriptions>
  </div>
}