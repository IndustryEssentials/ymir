import React, { useEffect, useState } from "react"
import { connect } from 'dva'
import styles from "./list.less"
import { Link, useHistory } from "umi"
import { Form, Input, Table, Modal, Row, Col, Tooltip, Pagination, Space, Empty, } from "antd"
import {
  SearchOutlined,
} from "@ant-design/icons"

import { format } from "@/utils/date"
import t from "@/utils/t"
import { percent } from '@/utils/number'
import { getTimes, getModelImportTypes } from '@/constants/query'
import EditBox from "@/components/form/editBox"
import { ShieldIcon, VectorIcon, TipsIcon, TreeIcon, EditIcon, DeleteIcon, FileDownloadIcon, TrainIcon } from "@/components/common/icons"
import Actions from "@/components/table/actions"
import TypeTag from "@/components/task/typeTag"
import { ArrowDownIcon, ArrowRightIcon } from "../common/icons"

const { confirm } = Modal
const { useForm } = Form

function Model({ pid, modelList, versions, getModels, getVersions, delModel, updateModel, query, updateQuery, resetQuery }) {
  const history = useHistory()
  const { name } = history.location.query
  const [models, setModels] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [current, setCurrent] = useState({})
  let [lock, setLock] = useState(true)

  /** use effect must put on the top */
  useEffect(() => {
    if (history.action !== 'POP') {
      initState()
    }
    setLock(false)
  }, [history.location])

  useEffect(() => {
    setModels(modelList.items)
    setTotal(modelList.total)
  }, [modelList])


  useEffect(async () => {
    if (name) {
      await updateQuery({ ...query, name })
      form.setFieldsValue({ name })
    }
    setLock(false)
  }, [name])

  useEffect(() => {
    if (!lock) {
      getData()
    }
  }, [query, lock])

  async function initState() {
    await resetQuery()
    form.resetFields()
 }

  const types = getModelImportTypes()

  const times = getTimes()

  const columns = [
    {
      title: showTitle("model.column.name"),
      dataIndex: "versionName",
      className: styles[`column_name`],
      render: (name, { id }) => (
        <Link to={`/home/model/detail/${id}`}>{name}</Link>
      ),
      ellipsis: true,
    },
    {
      title: showTitle("model.column.source"),
      dataIndex: "taskType",
      render: (type) => <TypeTag types={getModelImportTypes()} type={type} />,
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
      render: map => <span title={map}>{percent(map)}</span>,
      align: 'center',
    },
    {
      title: showTitle("model.column.create_time"),
      key: "create_datetime",
      dataIndex: "create_datetime",
      render: (datetime) => format(datetime),
      sorter: true,
      width: 200,
      align: 'center',
    },
    {
      title: showTitle("model.column.action"),
      key: "action",
      dataIndex: "action",
      render: (text, record) => <Actions menus={actionMenus(record)} showCount={4} />,
      className: styles.tab_actions,
      align: "center",
      width: "280px",
    },
  ]

  const tableChange = ({ current, pageSize }, filters, sorters = {}) => {
  }

  const listChange = ({ current, pageSize }) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    updateQuery({ ...query, limit, offset })
  }

  
  async function showVersions(id) {
    if (!models.some(item => item.id === id && item.showVersions)) {
      const result = await getVersions(id)
      if (!result) {
        return
      }
    }
    setModels(models.map(item => {
      if (item.id === id) {
        item.showVersions = !item.showVersions
      }
      return item
    }))
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  async function getData() {
    await getModels(pid, query)
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
        key: "train",
        label: t("dataset.action.train"),
        onclick: () => history.push(`/home/task/train?mid=${id}`),
        icon: <TrainIcon />,
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

  const search = (values) => {
    const name = values.name
    if (typeof name === 'undefined') {
      updateQuery({ ...query, ...values, })
    } else {
      setTimeout(() => {
        if (name === form.getFieldValue('name')) {
          updateQuery({ ...query, name, })
        }
      }, 1000)
    }
  }

  const renderGroups = (<>
    <div className={styles.groupList}>
      {models.length ? models.map(group => <div className={styles.groupItem} key={group.id}>
        <Row className={styles.groupTitle}>
          <Col flex={1}><span className={styles.foldBtn} onClick={() => showVersions(group.id)}>{ group.showVersions ? <ArrowDownIcon /> :<ArrowRightIcon />} </span>
            <span className={styles.groupName}>{group.name}</span></Col>
          <Col><Space>
            <a onClick={edit} title={t('common.modify')}><EditIcon /></a>
            <a onClick={del} title={t('common.del')}><DeleteIcon /></a>
          </Space></Col>
        </Row>
        <div className={styles.groupTable} hidden={!group.showVersions}>
          <Table
            dataSource={versions[group.id]}
            onChange={tableChange}
            rowKey={(record) => record.id}
            rowClassName={(record, index) => index % 2 === 0 ? styles.normalRow : styles.oddRow}
            columns={columns}
            pagination={false}
          />
        </div>
      </div>) : <Empty />}
    </div>
    <Pagination className={styles.pager} showQuickJumper showSizeChanger total={total} defaultCurrent={1} defaultPageSize={query.limit} onChange={listChange} />
  </>)

  return (
    <div className={styles.model}>
      <div className={styles.list}>
        <div className={styles.search}>
          <Form
            name='queryForm'
            form={form}
            labelCol={{ flex: '100px' }}
            initialValues={{ time: query.time, name: name || query.name }}
            onValuesChange={search}
            colon={false}
          >
            <Row>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item name="name" label={t('model.query.name')}>
                  <Input placeholder={t("model.query.name.placeholder")} style={{ width: '80%' }} allowClear suffix={<SearchOutlined />} />
                </Form.Item>
              </Col>
            </Row>
          </Form>
        </div>

        {renderGroups}
      </div>
      <EditBox record={current} max={80} action={saveName}>
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
    </div>
  )
}

const props = (state) => {
  return {
    logined: state.user.logined,
    query: state.model.query,
    modelList: state.model.models,
    versions: state.model.versions,
  }
}

const actions = (dispatch) => {
  return {
    getModels: (pid, query) => {
      return dispatch({
        type: 'model/getModels',
        payload: { pid, query },
      })
    },
    getVersions: (gid) => {
      return dispatch({
        type: 'model/getModelVersions',
        payload: gid,
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
    updateQuery: (query) => {
      return dispatch({
        type: 'model/updateQuery',
        payload: query,
      })
    },
    resetQuery: () => {
      return dispatch({
        type: 'model/resetQuery',
      })
    },
  }
}

export default connect(props, actions)(Model)
