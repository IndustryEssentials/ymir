import React, { useEffect, useState } from "react"
import { Table } from "antd"
import { useSelector } from "umi"

import t from "@/utils/t"

import s from "./index.less"
import { getDatasetColumns, getModelColumns } from "@/components/table/Columns"

function Panel({ list = [], customColumns, title = "", type = "dataset" }) {
  const [columns, setColumns] = useState([])
  const rows = useSelector(({ dataset, model }) => {
    const isModel = type !== "dataset"
    const res = isModel ? model.model : dataset.dataset
    console.log("list:", list)
    return list.length
      ? [
          ...list
            .map(({ label, id }) => {
              const result = res[id]
              return res[id]
                ? {
                    ...result,
                    label,
                    index: `${result.id}${new Date().getTime()}`,
                  }
                : null
            })
            .filter((item) => item),
        ]
      : []
  })

  useEffect(() => {
    const labelCol = {
      title: "iteration label",
      dataIndex: "label",
      render: (label) => t(label),
    }
    const cols = type === "dataset" ? getDatasetColumns() : getModelColumns()
    setColumns([labelCol, ...cols])
  }, [type])

  useEffect(() => customColumns && setColumns(customColumns), [customColumns])

  return (
    <div className={s.panel}>
      <div className={s.title}>{title}</div>
      <div className={s.content}>
        <Table
          dataSource={rows}
          columns={columns}
          rowKey={(record) => record.index}
          rowClassName={(_, index) => (index % 2 === 0 ? "" : "oddRow")}
          pagination={false}
        />
      </div>
    </div>
  )
}

export default Panel
