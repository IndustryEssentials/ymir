import React, { useEffect, useState } from "react"
import { Table } from "antd"
import { useSelector } from 'umi'

import t from "@/utils/t"

import s from "./index.less"
import getColumns from "@components/table/Columns"

function Panel({ list = [], customColumns, title = '', type = 'dataset' }) {

  const [columns, setColumns] = useState([])
  const rows = useSelector(({ dataset, model }) => {
    const isModel = type !== 'dataset'
    const res = isModel ? model.model: dataset.dataset
    return list.length ? [...(list.map(id => {
      const result = res[id]
      return res[id] ? {
        ...result,
        index: `${result.id}${new Date().getTime()}`,
      } : null
    }).filter(item => item))] : []
  })

  useEffect(() => setColumns(getColumns(type)), [type])

  useEffect(() => customColumns && setColumns(customColumns), [customColumns])

  return <div className={s.panel}>
    <div className={s.title}>{title}</div>
    <div className={s.content}>
      <Table
        dataSource={rows}
        columns={columns}
        rowKey={(record) => record.index}
        rowClassName={(_, index) => index % 2 === 0 ? '' : 'oddRow'}
        pagination={false}
      />
    </div>
  </div>
}

export default Panel
