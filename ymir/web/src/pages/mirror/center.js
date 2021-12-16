import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import styles from "./index.less"
import { Link, useHistory, useParams } from "umi"
import { Form, Button, Input, Select, Table, Menu, Dropdown, Space, Modal, ConfigProvider, Row, Col, Radio, Tooltip, } from "antd"
import {
  PlusOutlined,
  SearchOutlined,
  SyncOutlined,
} from "@ant-design/icons"
import moment from "moment"

import { numFormat } from "@/utils/number"
import { format, getUnixTimeStamp } from "@/utils/date"
import t from "@/utils/t"
import { getTimes, getModelImportTypes } from '@/constants/query'
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyState from '@/components/empty/model'
import EditBox from "../../components/form/editBox"
import { ImportIcon, ShieldIcon, VectorIcon, TipsIcon, More1Icon, TreeIcon, EditIcon, DeleteIcon, FileDownloadIcon } from "../../components/common/icons"
import Actions from "../../components/table/actions"
import TypeTag from "../../components/task/typeTag"

const { confirm } = Modal
const { useForm } = Form

const initQuery = {
  name: "",
  type: "",
  time: 0,
  offset: 0,
  limit: 20,
}

function Keyword({ getModels, delModel, updateModel }) {
  const { keyword } = useParams()
  const history = useHistory()
  const [models, setModels] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [query, setQuery] = useState(initQuery)
  const [current, setCurrent] = useState({})
  const [showAdd, setSowAdd] = useState(false)
  let [init, setInit] = useState(Boolean(keyword))

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

  const types = getModelImportTypes()

  const times = getTimes()

  const renderSource = (type, record) => {
    const target = types.find((t) => t.value === type)
    if (!target) {
      return type
    }

    if (target.value === 1) {
      // train
      return (
        <Link to={`/home/task/detail/${record.task_id}`}>{t('model.type.train')}: {record.task_name}</Link>
      )
    } else {
      return target.label
    }
  }

  const columns = [
    {
      title: showTitle("model.column.name"),
      key: "name",
      dataIndex: "name",
      className: styles[`column_name`],
      render: (name, { id }) => (
        <Link to={`/home/model/detail/${id}`}>{name}</Link>
      ),
      ellipsis: true,
    },
    {
      title: showTitle("model.column.source"),
      dataIndex: "source",
      render: (type, { task_id, task_name }) => <TypeTag types={getModelImportTypes()} type={type} id={task_id} name={task_name} />,
      ellipsis: true,
    },
    {
      title: showTitle("model.column.target"),
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
      title: showTitle("model.column.map"),
      dataIndex: "map",
      align: 'center',
    },
    {
      title: showTitle("model.column.create_time"),
      key: "create_datetime",
      dataIndex: "create_datetime",
      render: (datetime) => format(datetime),
      width: 200,
      align: 'center',
    },
    {
      title: showTitle("model.column.action"),
      key: "action",
      dataIndex: "action",
      render: (text, record) => <Actions menus={actionMenus(record)} />,
      className: styles.tab_actions,
      align: "center",
      width: "280px",
    },
  ]

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
    if (query.source !== "") {
      params.source = query.source
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
    const { items, total } = await getModels(params)
    if (items) {
      setModels(() => items)
      setTotal(total)
    }
  }

  const actionMenus = (record) => {
    const { id, name, url } = record
    return [
      {
        key: "verify",
        label: t("model.action.verify"),
        onclick: () => history.push(`/home/model/verify/${id}`),
        icon: <ShieldIcon />,
      },
      {
        key: "download",
        label: t("model.action.download"),
        link: url,
        target: '_blank',
        icon: <FileDownloadIcon />,
      },
      {
        key: "mining",
        label: t("dataset.action.mining"),
        onclick: () => history.push(`/home/task/mining?mid=${id}`),
        icon: <VectorIcon />,
      },
      {
        key: "history",
        label: t("dataset.action.history"),
        onclick: () => history.push(`/home/history/model/${id}`),
        icon: <TreeIcon />,
      },
      {
        key: "edit",
        label: t("dataset.action.edit"),
        onclick: () => edit(record),
        icon: <EditIcon />,
      },
      {
        key: "del",
        label: t("dataset.action.del"),
        onclick: () => del(id, name),
        className: styles.action_del,
        icon: <DeleteIcon />,
      },
    ]
  }

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const del = (id, name) => {
    confirm({
      icon: <TipsIcon style={{ color: 'rgb(242, 99, 123)' }} />,
      content: t("model.action.del.confirm.content", { name }),
      onOk: async () => {
        const result = await delModel(id)
        if (result) {
          setModels(models.filter((model) => model.id !== id))
          setTotal(old => old - 1)
          getData()
        }
      },
      okText: t('task.action.del'),
      okButtonProps: { style: { backgroundColor: 'rgb(242, 99, 123)', borderColor: 'rgb(242, 99, 123)', } }
    })
  }


  const saveName = async (record, name) => {
    const result = await updateModel(record.id, name)
    if (result) {
      setModels((models) =>
        models.map((model) => {
          if (model.id === record.id) {
            model.name = name
          }
          return model
        })
      )
    }
  }

  const add = () => {
    setSowAdd(true)
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

  // const addBtn = (
  //   <Button type="primary" onClick={add}>
  //     <PlusOutlined /> {t("model.import.label")}
  //   </Button>
  // )

  return (
    <div className={styles.model}>
      <Breadcrumbs />
      <div className={styles.list}>
        <div className={styles.search}>
          <Form
            name='queryForm'
            form={form}
            // layout="inline"
            labelCol={{ flex: '100px' }}
            initialValues={{ source: "", time: 0, name: keyword || "" }}
            onValuesChange={search}
            size='large'
            colon={false}
          >
            <Row>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item name="name" label={t('model.query.name')}>
                  <Input placeholder={t("model.query.name.placeholder")} style={{ width: '80%' }} allowClear suffix={<SearchOutlined />} />
                </Form.Item>
              </Col>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item
                  name="time"
                  label={t("model.column.create_time")}
                >
                  <Radio.Group options={times} optionType="button"></Radio.Group>
                </Form.Item></Col>
            </Row>
          </Form>
        </div>

        {/* <Space hidden={true} className={styles.actions}>
        {addBtn}
      </Space> */}
        <Row className={styles.refresh}>
          <Col flex={1}>
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
          <ConfigProvider renderEmpty={() => <EmptyState />}>
            <Table
              dataSource={models}
              onChange={({ current, pageSize }) =>
                pageChange({ current, pageSize })
              }
              rowKey={(record) => record.id}
              pagination={{
                showQuickJumper: true,
                showSizeChanger: true,
                total: total,
                // total: 500,
                defaultPageSize: query.limit,
                showTotal: (total) => t("model.pager.total.label", { total }),
                defaultCurrent: 1,
              }}
              columns={columns}
            ></Table>
          </ConfigProvider>
        </div>
      </div>
      <EditBox record={current} action={saveName}>
        {current.source ? <Form.Item label={t('model.column.source')}>
          <TypeTag types={types} type={current.source} id={current.id} name={current.task_name} />
        </Form.Item> : null}
        {current.keywords ? <Form.Item label={t('model.column.target')}>
          {t('dataset.column.keyword.label', { keywords: current.keywords.join(', '), total: current.keywords.length })}
        </Form.Item> : null}
        <Form.Item label={t('model.column.map')}>
          {current.map}
        </Form.Item>
      </EditBox>
      {/* <Add visible={showAdd} type='local' cancel={() => setSowAdd(false)} ok={() => { resetQuery(); getData() }} /> */}
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
    getModels: (payload) => {
      return dispatch({
        type: 'model/getModels',
        payload,
      })
    },
    delModel: (payload) => {
      return dispatch({
        type: 'model/delModel',
        payload,
      })
    },
    updateModel: (id, name) => {
      return dispatch({
        type: 'model/updateModel',
        payload: { id, name },
      })
    },
  }
}

export default connect(props, actions)(Keyword)
