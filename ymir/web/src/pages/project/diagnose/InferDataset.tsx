import useFetch from "@/hooks/useFetch"
import { Card, Table } from "antd"
import React from "react"

import s from './index.less'

const InferDataset: React.FC = () => {
  const [datasets, getDatasets] = useFetch('dataset/getDatasets', [])
  const columns = [
    {}
  ]
  return <div className={s.inferDataset}>
    <Card title="推理结果">
      <Table
        columns={columns}
        dataSource={datasets}
      />
    </Card>
  </div>
}

export default InferDataset
