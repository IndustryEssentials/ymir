import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import { Link, useHistory, useParams, getLocale, } from "umi"
import { Form, Button, Input, Table, Space, Modal, ConfigProvider, Progress, Radio, Row, Col, } from "antd"
import {
  SearchOutlined,
  SyncOutlined,
} from "@ant-design/icons"
import moment from "moment"

import { format, getUnixTimeStamp, calDuration } from "@/utils/date"
import t from "@/utils/t"
import Empty from '@/components/empty/default'
import { TASKSTATES, TASKTYPES } from "../../constants/task"
import { getTaskTypes, getTimes, getTaskStates } from '@/constants/query'
import Breadcrumbs from "../../components/common/breadcrumb"
import styles from "./index.less"
import { CopyIcon, DeleteIcon, EditIcon, FlagIcon, InprogressIcon, ScreenIcon, SearchEyeIcon, StopIcon, TaggingIcon, TipsIcon, TrainIcon, VectorIcon } from "../../components/common/icons"
import EditBox from "../../components/form/editBox"
import StateTag from "../../components/task/stateTag"
import RenderProgress from "../../components/common/progress"
import Actions from "../../components/table/actions"
import Confirm from "../../components/common/dangerConfirm"
import Terminate from "./components/terminate"

const { confirm } = Modal
const { useForm } = Form

const initQuery = {
  name: "",
  type: "",
  time: 0,
  offset: 0,
  limit: 20,
}

function Task({ getTasks, delTask, updateTask, stopTask, getLabelData }) {
  const { keyword } = useParams()
  const history = useHistory()
  const [tasks, setTasks] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [query, setQuery] = useState(initQuery)
  const [current, setCurrent] = useState({})
  const terminateRef = useRef(null)
  let [init, setInit] = useState(Boolean(keyword))
  // const [showAdd, setSowAdd] = useState(false)

  /** use effect must put on the top */
  useEffect(() => {
    if (init) {
      setInit(false)
      return
    }
    getData()
  }, [query])

  useEffect(() => {
    if (keyword) {
      setQuery(old => ({ ...old, name: keyword }))
      form.setFieldsValue({ name: keyword })
    }
  }, [keyword])

  const types = getTaskTypes()
  const states = getTaskStates()
  const times = getTimes()

  const columns = [
    {
      title: showTitle("task.column.name"),
      dataIndex: "name",
      // width: "240px",
      className: styles[`column_name`],
      render: (name, { id }) => (
        <Link to={`/home/task/detail/${id}`}>{name}</Link>
      ),
      ellipsis: true,
    },
    // { title: "ID", key: "id", dataIndex: "id", width: 100, },
    {
      title: showTitle("task.column.type"),
      dataIndex: "type",
      width: 160,
      align: 'center',
      render: (type) => (types.find((t) => t.value === type))?.label,
    },
    {
      title: showTitle("task.column.state"),
      dataIndex: "state",
      align: 'center',
      render: (state, record) => RenderProgress(state, record),
    },
    {
      title: showTitle("task.column.create_time"),
      dataIndex: "create_datetime",
      width: 200,
      sorter: true,
      render: (datetime) => format(datetime),
    },
    {
      title: showTitle("task.column.duration"),
      dataIndex: "duration",
      width: 200,
      sorter: true,
      align: 'center',
      render: (seconds) => calDuration(seconds, getLocale()),
    },
    {
      title: showTitle("task.column.action"),
      key: "action",
      dataIndex: 'actions',
      render: (text, record) => <Actions menus={actionMenus(record)} />,
      className: styles.tab_actions,
      align: "left",
      width: 240,
    },
  ]

  const addMore = [
    {
      key: "filter",
      label: t("task.add.option.filter"),
      link: '/home/task/filter',
      icon: <ScreenIcon className={styles.addBtnIcon} />,
    },
    {
      key: "train",
      label: t("task.add.option.train"),
      link: '/home/task/train',
      icon: <TrainIcon className={styles.addBtnIcon} />,
    },
    {
      key: "mine",
      label: t("task.add.option.mine"),
      link: '/home/task/mining',
      icon: <VectorIcon className={styles.addBtnIcon} />,
    },
    {
      key: "label",
      label: t("task.add.option.label"),
      link: '/home/task/label',
      icon: <TaggingIcon className={styles.addBtnIcon} />,
    },
  ]


  const tableChange = ({ current, pageSize }, filters, sorters = {}) => {
    console.log('tabel chagne: ', sorters, calDuration(365000, getLocale()))
    const orders = {
      'duration': 2,
      'create_datetime': 3,
    }
    const limit = pageSize
    const offset = (current - 1) * pageSize
    const is_desc = sorters.order === 'ascend' ? false : true
    const order_by = sorters.order ? (orders[sorters.field] || 1) : undefined
    setQuery((old) => ({ ...old, limit, offset, is_desc, order_by }))
  }

  function showTitle(str) {
    return <div style={{ textAlign: 'center' }}><strong>{t(str)}</strong></div>
  }
  async function getData() {
    let params = {
      offset: query.offset,
      limit: query.limit,
      is_desc: query.is_desc,
      order_by: query.order_by,
    }
    if (query.type !== "") {
      params.type = query.type
    }
    if (query.state !== "") {
      params.state = query.state
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
    const { items, total } = await getTasks(params)
    if (items) {
      setTasks(() => items)
      setTotal(total)
    }
  }

  const del = (id, name) => {
    Confirm({
      content: t("task.action.del.confirm.content", { name }),
      onOk: async () => {
        const result = await delTask(id)
        if (result) {
          setTasks(tasks.filter((task) => task.id !== id))
          setTotal(total => total - 1)
          getData()
        }
      },
      okText: t('task.action.del'),
    })
  }
  const stop = (task) => {
    terminateRef.current.confirm(task)
  }

  function terminateOk() {
    getData()
  }

  const copy = (record) => {
    const { type } = record
    const { key } = getTaskTypes().find(task => task.value === type)
    history.push({ pathname: `/home/task/${key}`,  state: { record } })
  }

  const getLabels = (id, name) => {
    Confirm({
      content: t("task.action.getlabels.confirm.content", { name }),
      onOk: async () => {
        const result = await stopTask(id)
        if (result) {
          getData()
        }
      },
      okText: t('task.action.labeldata'),
    })
  }

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const saveName = async (record, name) => {
    const result = await updateTask(record.id, name)
    if (result) {
      setTasks((tasks) =>
        tasks.map((task) => {
          if (task.id === record.id) {
            task.name = name
          }
          return task
        })
      )
    }
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
        // console.log('compact: ', name, form.getFieldValue('name'))
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

  const actionMenus = (record) => {
    const { id, name, state, type } = record
    const menus = [
      {
        key: "copy",
        label: t("task.action.copy"),
        onclick: () => copy(record),
        icon: <CopyIcon />,
      },
      {
        key: "stop",
        label: t("task.action.terminate"),
        onclick: () => stop(record),
        hidden: () => {
          return [TASKSTATES.PENDING, TASKSTATES.DOING].indexOf(state) < 0
        },
        icon: <StopIcon />,
      },
      {
        key: "del",
        label: t("task.action.del"),
        onclick: () => del(id, name),
        hidden: () => {
          return [TASKSTATES.FINISH, TASKSTATES.FAILURE].indexOf(state) < 0
        },
        icon: <DeleteIcon />,
      },
      {
        key: "edit",
        label: t("task.action.edit"),
        onclick: () => edit(record),
        icon: <EditIcon />,
      },
      {
        key: "labelplatform",
        label: t("task.action.labelplatform"),
        link: '/lsf/',
        target: '_blank',
        // onclick: () => history.push(`/lsf/`),
        hidden: () => {
          return TASKTYPES.LABEL !== type
        },
        icon: <FlagIcon />,
      },
    ]
    return menus
  }

  const addBtn = addMore.map(action => <Button
    className={action.className}
    key={action.key}
    icon={action.icon}
    type='primary'
    onClick={() => history.push(action.link)}
  >{action.label}</Button>)

  const addBoxes = (
    <div className={styles.addBoxes}>
      <Row gutter={20}>
        {addMore.map(action => <Col span={6} key={action.key}>
          <Link className={styles.addBoxBtn} to={action.link}>
            <div className={styles.addBtnIcon}>{action.icon}</div><div>{t('task.add.label')}{action.label}</div>
          </Link>
        </Col>)}
      </Row>
    </div>
  )

  const renderQuery = (
    <div className={styles.search}>
      <Form
        name='queryForm'
        form={form}
        // layout="inline"
        labelCol={{ flex: '100px' }}
        initialValues={{ type: "", state: '', time: 0, name: keyword || "" }}
        onValuesChange={search}
        size='large'
        colon={false}
      // onFinish={search}
      >
        <Row>
          <Col className={styles.queryColumn} span={12}>
            <Form.Item name="name" label={t('task.query.name')}>
              <Input placeholder={t("task.query.name.placeholder")} style={{ width: '80%' }} allowClear suffix={<SearchOutlined />} />
            </Form.Item>
          </Col>
          <Col className={styles.queryColumn} span={12}>
            <Form.Item
              name="type"
              label={t("task.column.type")}
            >
              <Radio.Group options={types} optionType='button'></Radio.Group>
            </Form.Item></Col>
          <Col className={styles.queryColumn} span={12}>
            <Form.Item
              name="state"
              label={t("task.column.state")}
            >
              <Radio.Group options={states} optionType='button'></Radio.Group>
            </Form.Item>
          </Col>
          <Col className={styles.queryColumn} span={12}>
            <Form.Item
              name="time"
              label={t("task.column.create_time")}
            >
              <Radio.Group options={times} optionType="button"></Radio.Group>
            </Form.Item></Col>
        </Row>

      </Form>
    </div>

  )

  return (
    <div className={styles.task}>
      <Breadcrumbs />
      {tasks.length ? (
        <Space className={styles.actions}>
          {addBtn}
        </Space>
      ) : addBoxes
      }

      <div className={styles.list}>
        {renderQuery}
        <div className={styles.refresh}>
          <Button
            type='text'
            icon={<SyncOutlined style={{ color: 'rgba(0, 0, 0, 0.45)' }} />}
            title={'Refresh'}
            onClick={() => getData()}
          ></Button>
        </div>
        <ConfigProvider renderEmpty={() => <Empty />}>
          <Table
            dataSource={tasks}
            onChange={tableChange}
            rowKey={(record) => record.id}
            rowClassName={(record, index) => index % 2 === 0 ? styles.normalRow : styles.oddRow}
            pagination={{
              showQuickJumper: true,
              showSizeChanger: true,
              total: total,
              // total: 500,
              defaultPageSize: query.limit,
              showTotal: (total) => t("task.pager.total.label", { total }),
              defaultCurrent: 1,
            }}
            columns={columns}
          ></Table>
        </ConfigProvider>
      </div>
      <EditBox record={current} action={saveName}>
        {current.type ? <Form.Item
          label={t('task.column.type')}
        >
          {(types.find((t) => t.value === current.type))?.label}
        </Form.Item> : null}
        {current.state ? <Form.Item
          label={t('task.detail.state.title')}
        >
          <StateTag mode='text' state={current.state} />
        </Form.Item> : null}
      </EditBox>
      <Terminate ref={terminateRef} ok={terminateOk} />
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
    getTasks: (payload) => {
      return dispatch({
        type: 'task/getTasks',
        payload,
      })
    },
    delTask: (payload) => {
      return dispatch({
        type: 'task/deleteTask',
        payload,
      })
    },
    stopTask: (id) => {
      return dispatch({
        type: 'task/stopTask',
        payload: id,
      })
    },
    getLabelData: (id) => {
      return dispatch({
        type: 'task/getLabelData',
        payload: id,
      })
    },
    updateTask: (id, name) => {
      return dispatch({
        type: 'task/updateTask',
        payload: { id, name },
      })
    },
  }
}

export default connect(props, actions)(Task)
