import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import styles from "./index.less"
import { Link, useHistory, useLocation, useParams } from "umi"
import { Form, Button, Input, Select, Table, Menu, Dropdown, Space, Modal, ConfigProvider, Row, Col, Radio, Tag, Tooltip, } from "antd"
import {
  SearchOutlined,
  SyncOutlined,
} from "@ant-design/icons"
import moment from "moment"

import { numFormat } from "@/utils/number"
import { format, getUnixTimeStamp } from "@/utils/date"
import t from "@/utils/t"

import Add from './add'
import { TASKSTATES } from '@/constants/task'
import { getDatasetTypes, getTimes } from '@/constants/query'
import { getSetStates } from '@/constants/column'
import Breadcrumbs from "../../components/common/breadcrumb"
import EmptyState from '@/components/empty/dataset'
import { ImportIcon, ScreenIcon, TaggingIcon, TrainIcon, VectorIcon, TipsIcon, More1Icon } from "../../components/common/icons"
import StateTag from "../../components/task/stateTag"
import EditBox from "../../components/form/editBox"
import Rect from '@/components/guide/rect'
import Guide from "../../components/guide/guide"
import RenderProgress from "../../components/common/progress"

const { confirm } = Modal
const { useForm } = Form

const initQuery = {
  name: "",
  type: "",
  time: 0,
  offset: 0,
  limit: 20,
}

function Dataset({ getDatasets, delDataset, updateDataset }) {
  const { keyword } = useParams()
  const location = useLocation()
  const history = useHistory()
  const [datasets, setDatasets] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [selectedIds, setSelectedIds] = useState([])
  const [selectedAssets, setSelectedAssets] = useState(0)
  const [query, setQuery] = useState(initQuery)
  const [current, setCurrent] = useState({})
  const [showAdd, setShowAdd] = useState(false)
  let [init, setInit] = useState(Boolean(keyword))

  const types = getDatasetTypes()
  const times = getTimes()
  const states = getSetStates()

  /** use effect must put on the top */
  useEffect(() => {
    if (keyword) {
      setQuery(old => ({ ...old, name: keyword }))
      form.setFieldsValue({ name: keyword })
    }
  }, [keyword])

  useEffect(() => {
    if (init) {
      setInit(false)
      return
    }
    getData()
  }, [query])

  useEffect(() => {
    setSelectedAssets(
      datasets.reduce(
        (sum, dataset) =>
          selectedIds.indexOf(dataset.id) !== -1
            ? sum + dataset.asset_count
            : sum,
        0
      )
    )
  }, [selectedIds])

  useEffect(() => {
    if (location.state?.type) {
      setShowAdd(location.state.type === 'add')
      history.replace(location.pathname, {})
    }
  }, [location.state])


  const renderSource = (type, record) => {
    const target = types.find((t) => t.value === type)
    if (!target) {
      return type
    }

    if ([2, 3, 4].indexOf(target.value) >= 0) {
      // train
      return (
        <Link to={`/home/task/detail/${record.task_id}`}>{t(`dataset.action.${target.key}`)}: {record.task_name}</Link>
      )
    } else {
      return target.label
    }
  }

  const columns = [
    {
      title: showTitle("dataset.column.name"),
      key: "name",
      dataIndex: "name",
      className: styles[`column_name`],
      render: (name, { id, state }) => state === TASKSTATES.FINISH ? (
        <Link to={`/home/dataset/detail/${id}`}>{name}</Link>
      ) : name,
      ellipsis: true,
    },
    {
      title: showTitle("dataset.column.source"),
      dataIndex: "type",
      render: renderSource,
      ellipsis: true,
    },
    {
      title: showTitle("dataset.column.asset_count"),
      dataIndex: "asset_count",
      render: (num) => numFormat(num),
      width: 120,
    },
    {
      title: showTitle("dataset.column.keyword"),
      dataIndex: "keywords",
      render: (keywords) => {
        const label = t('dataset.column.keyword.label', { keywords: keywords.join(', '), total: keywords.length })
        return <Tooltip placement='left' title={label}
          color='white' overlayInnerStyle={{ color: 'rgba(0,0,0,0.45)', fontSize: 12 }}
          mouseEnterDelay={0.5}
        >{label}</Tooltip>
      },
      ellipsis: {
        showTitle: false,
      },
    },
    {
      title: showTitle('dataset.column.state'),
      dataIndex: 'state',
      render: (state, record) => RenderProgress(state, record, true),
      // width: 60,
    },
    {
      title: showTitle("dataset.column.create_time"),
      key: "create_datetime",
      dataIndex: "create_datetime",
      render: (datetime) => format(datetime),
      width: 180,
    },
    {
      title: showTitle("dataset.column.action"),
      key: "action",
      dataIndex: "action",
      render: (text, record) => actions(record),
      className: styles.tab_actions,
      align: "center",
      width: 300,
    },
  ]

  const moreActionsList = (record) => {
    const { id, name } = record
    return [
      {
        key: "history",
        label: t("dataset.action.history"),
        onclick: () => history.push(`/home/history/dataset/${id}`),
      },
      {
        key: "edit",
        label: t("dataset.action.edit"),
        onclick: () => edit(record),
      },
      {
        key: "del",
        label: t("dataset.action.del"),
        onclick: () => del(id, name),
        className: styles.action_del,
      },
    ]
  }

  const pageChange = ({ current, pageSize }) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery((old) => ({ ...old, limit, offset }))
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  async function getData() {
    let params = {
      offset: query.offset,
      limit: query.limit,
    }
    if (query.type !== "") {
      params.type = query.type
    }
    if (query.time) {
      const now = moment()
      const today = moment([now.year(), now.month(), now.date()])
      const startTime = today.subtract(query.time - 1, 'd')
      params.end_time = getUnixTimeStamp(now)
      params.start_time = getUnixTimeStamp(startTime)
    }
    if (query.name) {
      params.name = query.name
    }
    const { items, total } = await getDatasets(params)
    if (items) {
      setDatasets(() => items)
      setTotal(total)
      setSelectedIds([])
    }
  }

  const del = (id, name) => {
    confirm({
      icon: <TipsIcon style={{color: 'rgb(242, 99, 123)'}} />,
      content: t("dataset.action.del.confirm.content", { name }),
      onOk: async () => {
        const result = await delDataset(id)
        if (result) {
          setDatasets(datasets.filter((dataset) => dataset.id !== id))
          setTotal(total => total - 1)
          getData()
        }
      },
      okText: t('task.action.del'),
      okButtonProps: { style: { backgroundColor: 'rgb(242, 99, 123)', borderColor: 'rgb(242, 99, 123)',  }}
    })
  }


  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const saveName = async (record, name) => {
    const result = await updateDataset(record.id, name)
    if (result) {
      setDatasets((datasets) =>
        datasets.map((dataset) => {
          if (dataset.id === record.id) {
            dataset.name = name
          }
          return dataset
        })
      )
    }
  }

  const getSelectedIds = () => {
    return selectedIds.join("|")
  }

  const add = () => {
    setShowAdd(true)
  }


  const search = (values) => {
    const name = values.name
    if (typeof name === 'undefined') {
      setQuery((old) => ({
        ...old,
        ...values,
        offset: initQuery.offset,
      }))
    } else {
      setTimeout(() => {
        if (name === form.getFieldValue('name')) {
          setQuery((old) => ({
            ...old,
            name,
            offset: initQuery.offset,
          }))
        }
      }, 1000)
    }
  }

  const resetQuery = () => {
    setQuery(initQuery)
    form.resetFields()
  }

  function isImporting(state) {
    return [TASKSTATES.PENDING, TASKSTATES.DOING].indexOf(state) >= 0
  }

  function isImportFail(state) {
    return TASKSTATES.FAILURE === state
  }

  function isImported(state) {
    return TASKSTATES.FINISH === state
  }

  function renderDel(record) {
    const del = moreActionsList(record).find(action => action.key === 'del')
    return <Button type='link' className={del.className} onClick={del.onclick}>{del.label}</Button>
  }

  const addBtn = (
    <Button type="primary" onClick={add}>
      <ImportIcon /> {t("dataset.import.label")}
    </Button>
  )

  const actions = (record) => {
    return isImported(record.state) ? (
      <Space size={4}>

        <Link className={styles.action} to={`/home/task/filter/${record.id}`}>
          <ScreenIcon className={styles.addBtnIcon} />{t("dataset.action.filter")}
        </Link> <span className={styles.l}>|</span>
        <Link className={styles.action} to={`/home/task/train/${record.id}`}>
          <TrainIcon className={styles.addBtnIcon} />{t("dataset.action.train")}
        </Link> <span className={styles.l}>|</span>
        <Link className={styles.action} to={`/home/task/mining/${record.id}`}>
          <VectorIcon className={styles.addBtnIcon} />{t("dataset.action.mining")}
        </Link> <span className={styles.l}>|</span>
        <Link className={styles.action} to={`/home/task/label/${record.id}`}>
          <TaggingIcon className={styles.addBtnIcon} />{t("dataset.action.label")}
        </Link>
        <Dropdown className={styles.action} overlay={moreActions(record)}>
          <More1Icon style={{ fontSize: 16, lineHeight: '16px', verticalAlign: 'middle', color: '#3BA0FF' }} />
        </Dropdown>
      </Space>
    ) : (isImportFail(record.state) ? renderDel(record) : null)
  }

  const moreActions = (record) => {
    return (
      <Menu>
        {moreActionsList(record).map((action) => (
          <Menu.Item
            className={action.className}
            key={action.key}
            onClick={action.onclick}
          >
            {action.label}
          </Menu.Item>
        ))}
      </Menu>
    )
  }

  return (
    <div className={styles.dataset}>
      <Breadcrumbs />
      <div className={styles.actions}>
        <Space>
          {addBtn}
          <Button
            style={{ display: selectedIds.length ? "" : "none" }}
            onClick={() => history.push("/home/task/train/" + getSelectedIds())}
          >
            {t("dataset.action.multi.train")}
          </Button>
          <Button
            style={{ display: selectedIds.length ? "" : "none" }}
            onClick={() => history.push("/home/task/mining/" + getSelectedIds())}
          >
            {t("dataset.action.multi.mine")}
          </Button>
          <Button
            style={{ display: selectedIds.length ? "" : "none" }}
            onClick={() => history.push("/home/task/filter/" + getSelectedIds())}
          >
            {t("dataset.action.filter")}
          </Button>
        </Space>
      </div>
      <div className={styles.list}>
        <div className={styles.search}>
          <Form
            name='queryForm'
            form={form}
            // layout="inline"
            labelCol={{ flex: '100px' }}
            initialValues={{ type: "", time: 0, name: keyword || "" }}
            onValuesChange={search}
            size='large'
            colon={false}
          // onFinish={search}
          >
            <Row>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item name="name" label={t('dataset.query.name')}>
                  <Input placeholder={t("dataset.query.name.placeholder")} style={{ width: '80%' }} allowClear suffix={<SearchOutlined />} />
                </Form.Item>
              </Col>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item
                  name="type"
                  label={t("dataset.column.source")}
                >
                  <Radio.Group options={types.filter(type => !type.hidden)} optionType='button'></Radio.Group>
                </Form.Item></Col>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item
                  name="time"
                  label={t("dataset.column.create_time")}
                >
                  <Radio.Group options={times} optionType="button"></Radio.Group>
                </Form.Item></Col>
            </Row>

          </Form>
        </div>


        <Row className={styles.refresh}>
          <Col flex={1}>
            <div style={{ display: selectedIds.length ? "" : "none" }}>
              {t("dataset.selected.label", {
                len: <span className={styles.blue}>{selectedIds.length}</span>,
                count: <span className={styles.blue}>{selectedAssets}</span>,
              })}
              <Button
                type="link"
                className={styles.bluelink}
                onClick={() => setSelectedIds([])}
              >
                {t("dataset.cancel.select")}
              </Button>
            </div>
          </Col>
          <Col>
            <Button
              type='text'
              icon={<SyncOutlined style={{ color: 'rgba(0, 0, 0, 0.45)' }} />}
              title={'Refresh'}
              onClick={() => getData()}
            ></Button>
          </Col>
        </Row>
        <div className={styles.table}>
          <ConfigProvider renderEmpty={() => <EmptyState add={add} />}>
            <Table
              dataSource={datasets}
              onChange={({ current, pageSize }) =>
                pageChange({ current, pageSize })
              }
              rowKey={(record) => record.id}
              rowClassName={(record, index) => index % 2 === 0 ? styles.normalRow : styles.oddRow}
              pagination={{
                showQuickJumper: true,
                showSizeChanger: true,
                total: total,
                // total: 500,
                defaultPageSize: query.limit,
                showTotal: (total) => t("dataset.pager.total.label", { total }),
                defaultCurrent: 1,
              }}
              rowSelection={{
                selectedRowKeys: selectedIds,
                onChange: (selected, rows) => {
                  setSelectedIds(selected)
                },
                getCheckboxProps: (record) => ({
                  disabled: isImporting(record.state) || isImportFail(record.state),
                })
              }}
              columns={columns}
            ></Table>
          </ConfigProvider>
        </div>
      </div>
      <Add visible={showAdd} id={location.state?.id} cancel={() => setShowAdd(false)} ok={() => { history.replace('/home/dataset'); resetQuery(); getData() }} />
      <EditBox record={current} action={saveName} dataType='dataset' />
    </div>
  )
}

const props = (state) => {
  return {
    logined: state.user.logined,
  }
}

const actions = (dispatch) => {
  return {
    getDatasets: (payload) => {
      return dispatch({
        type: 'dataset/getDatasets',
        payload,
      })
    },
    delDataset: (payload) => {
      return dispatch({
        type: 'dataset/delDataset',
        payload,
      })
    },
    updateDataset: (id, name) => {
      return dispatch({
        type: 'dataset/updateDataset',
        payload: { id, name },
      })
    },
  }
}

export default connect(props, actions)(Dataset)
