import React, { useEffect, useState } from "react"
import { connect } from 'dva'
import s from "../index.less"
import { useHistory, useLocation, useParams } from "umi"
import { Form, Table, Modal, ConfigProvider, Card, Space, Row, Col, Button, Popover, } from "antd"

import t from "@/utils/t"
import { tabs } from '@/constants/project'
import { EyeOnIcon } from "@/components/common/icons"

const HiddenList = ({ active }) => {
  const { id } = useParams()
  const [list, setHiddenList] = useState([])

  useEffect(() => {
    if (id) {
      // fetchHiddenList()
    }
  }, [id])

  const columns = [
    {
      title: showTitle("iteration.column.round"),
      dataIndex: "round",
      render: (round) => (t('iteration.round.label', { round })),
    },
    {
      title: showTitle("iteration.column.premining"),
      dataIndex: "miningDatasetLabel",
      render: (label, { versionName, miningDataset }) => renderPop(label, miningDataset),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.mining"),
      dataIndex: "miningResultDatasetLabel",
      render: (label, { miningResultDataset }) => renderPop(label, miningResultDataset),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.label"),
      dataIndex: "labelDatasetLabel",
      render: (label, { labelDataset }) => renderPop(label, labelDataset),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.test"),
      dataIndex: "testDatasetLabel",
      render: (label, { testDataset }) => renderPop(label, testDataset),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.merging"),
      dataIndex: "trainUpdateDatasetLabel",
      render: (label, { trainEffect, trainUpdateDataset }) => renderPop(label, trainUpdateDataset,
        <span className={s.extraTag}>{renderExtra(trainEffect)}</span>),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.training"),
      dataIndex: 'map',
      render: (map, { mapEffect }) => <div className={s.td}>
        <span>{map >= 0 ? percent(map) : null}</span>
        <span className={s.extraTag}>{renderExtra(mapEffect, true)}</span>
      </div>,
      align: 'center',
    },
  ]

  function renderPop(label, dataset = {}, extra) {
    return label
  }

  function renderExtra(value, showPercent = false) {
    const cls = value < 0 ? s.negative : (value > 0 ? s.positive : s.neutral)
    const label = showPercent ? percent(value) : value
    return isNumber(value) ? <span className={cls}>{label}</span> : null
  }


  async function fetchHiddenList() {
    const result = await func.getHiddenList(id)
    if (result) {
      const iters = fetchHandle(result)
      setHiddenList(iters)
    }
  }

  function fetchHandle(list) {
    return list
  }

  function multipleRestore() {

  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  return <><Space className={s.actions}>
    <Button type="primary" onClick={multipleRestore}>
      <EyeOnIcon /> {t("common.action.multiple.restore")}
    </Button>
  </Space>
    <div className={s.table}>
      <Table
        dataSource={list}
        pagination={false}
        rowKey={(record) => record.id}
        columns={columns}
      ></Table>
    </div>
  </>
}

const props = (state) => {
  return {
    logined: state.user.logined,
  }
}

const actions = (dispatch) => {
  return {
    getHiddenList(type, id) {
      return dispatch({
        type: 'dataset/getHiddenList',
        payload: { id, more: true },
      })
    }
  }
}

export default connect(props, actions)(HiddenList)
