import React, { useEffect, useState } from "react"
import { Table } from "antd"

import t from "@/utils/t"

import s from "./index.less"
import getColumns from "./columns"

function Panel({ list = [], customColumns, title = '', type = 'dataset' }) {

  const [columns, setColumns] = useState([])

  useEffect(() => setColumns(getColumns(type)), [type])

  useEffect(() => customColumns && setColumns(customColumns), [customColumns])

  return <div className={s.panel}>
    <div className={s.title}>{title}</div>
    <div className={s.content}>
      <Table
        dataSource={list}
        columns={columns}
        rowKey={(record) => record?.id}
        rowClassName={(_, index) => index % 2 === 0 ? '' : 'oddRow'}
        pagination={false}
      />
    </div>
  </div>
}

export default Panel
