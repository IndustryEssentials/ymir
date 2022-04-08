import React, { useEffect, useState, useRef } from "react"
import { connect } from 'dva'
import styles from "./list.less"
import { Link, useHistory } from "umi"
import { Form, Input, Table, Modal, Row, Col, Tooltip, Pagination, Space, Empty, Button, } from "antd"
import {
  SearchOutlined,
} from "@ant-design/icons"

import { format } from "@/utils/date"
import { states } from '@/constants/model'
import t from "@/utils/t"
import { percent } from '@/utils/number'
import { getTimes, getModelImportTypes } from '@/constants/query'
import RenderProgress from "@/components/common/progress"
import EditBox from "@/components/form/editBox"
import { ShieldIcon, VectorIcon, TipsIcon, TreeIcon, EditIcon, DeleteIcon, FileDownloadIcon, TrainIcon, WajueIcon } from "@/components/common/icons"
import Actions from "@/components/table/actions"
import TypeTag from "@/components/task/typeTag"
import Del from "./del"
import DelGroup from "./delGroup"
import { ArrowDownIcon, ArrowRightIcon, ImportIcon } from "../common/icons"

const { confirm } = Modal
const { useForm } = Form

function Model({ pid, modelList, versions, getModels, getVersions, updateModel, query, updateQuery, resetQuery }) {
  const history = useHistory()
  const { name } = history.location.query
  const [models, setModels] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [current, setCurrent] = useState({})
  let [lock, setLock] = useState(true)
  const delRef = useRef(null)
  const delGroupRef = useRef(null)

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

  useEffect(() => {
    const hasModel = Object.keys(versions).length
    const emptyModel = Object.values(versions).some(models => !models.length)
    if (hasModel && emptyModel) {
      getData()
    }
  }, [versions])

  useEffect(() => {
    Object.keys(versions).forEach(gid => {
      const vss = versions[gid]
      const needReload = vss.some(ds => ds.needReload)
      if (needReload) {
        fetchVersions(gid, true)
      }
    })
  }, [versions])
  
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
        <Link to={`/home/project/${pid}/model/${id}`}>{name}</Link>
      ),
      ellipsis: true,
    },
    {
      title: showTitle("model.column.source"),
      dataIndex: "taskType",
      render: (type) => <TypeTag types={getModelImportTypes()} type={type} />,
    },
    {
      title: showTitle("model.column.map"),
      dataIndex: "map",
      render: map => <span title={map}>{percent(map)}</span>,
      align: 'center',
    },
    {
      title: showTitle('dataset.column.state'),
      dataIndex: 'state',
      render: (state, record) => RenderProgress(state, record, true),
      // width: 60,
    },
    {
      title: showTitle("model.column.create_time"),
      dataIndex: "createTime",
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
      fetchVersions(id)
    }
    setModels(models.map(item => {
      if (item.id === id) {
        item.showVersions = !item.showVersions
      }
      return item
    }))
  }

  
  async function fetchVersions(id, force) {
    await getVersions(id, force)
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  async function getData() {
    await getModels(pid, query)
  }

  const actionMenus = (record) => {
    const { id, name, url, state, versionName } = record
    const actions = [
      {
        key: "verify",
        label: t("model.action.verify"),
        onclick: () => history.push(`/home/project/${pid}/model/${id}/verify`),
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
        onclick: () => history.push(`/home/task/mining/${pid}?mid=${id}`),
        icon: <VectorIcon />,
      },
      {
        key: "train",
        label: t("dataset.action.train"),
        onclick: () => history.push(`/home/task/train/${pid}?mid=${id}`),
        icon: <TrainIcon />,
      },
      {
        key: "inference",
        label: t("dataset.action.inference"),
        onclick: () => history.push(`/home/task/inference/${pid}?mid=${id}`),
        icon: <WajueIcon />,
      },
      
    ]
    const delAction = {
      key: "del",
      label: t("dataset.action.del"),
      onclick: () => del(id, `${name} ${versionName}`),
      className: styles.action_del,
      icon: <DeleteIcon />,
    }
    return isValidModel(state) ? [...actions, delAction] : [delAction]
  }

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const delGroup = (id, name) => {
    delGroupRef.current.del(id, name)
  }
  const del = (id, name) => {
    delRef.current.del(id, name)
  }

  const delOk = (id) => {
    getVersions(id, true)
  }

  const delGroupOk = () => {
    getData()
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

  function isValidModel(state) {
    return states.VALID === state
  }

  function add() {
    history.push(`/home/model/import/${pid}`)
  }

  const addBtn = (
    <Button type="primary" onClick={add}>
      <ImportIcon /> {t("model.import.label")}
    </Button>
  )

  const renderGroups = (<>
    <div className={styles.groupList}>
      {models.length ? models.map(group => <div className={styles.groupItem} key={group.id}>
        <Row className={styles.groupTitle}>
          <Col flex={1}><span className={styles.foldBtn} onClick={() => showVersions(group.id)}>{group.showVersions ? <ArrowDownIcon /> : <ArrowRightIcon />} </span>
            <span className={styles.groupName}>{group.name}</span></Col>
          <Col><Space>
            <a onClick={() => edit(group)} title={t('common.modify')}><EditIcon /></a>
            <a onClick={() => delGroup(group.id, group.name)} title={t('common.del')}><DeleteIcon /></a>
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
      <div className={styles.actions}>
        <Space>
          {addBtn}
        </Space>
      </div>
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
      <EditBox record={current} max={80} action={saveName}></EditBox>
      <DelGroup ref={delGroupRef} ok={delGroupOk} />
      <Del ref={delRef} ok={delOk} />
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
        type: 'model/getModelGroups',
        payload: { pid, query },
      })
    },
    getVersions: (gid, force) => {
      return dispatch({
        type: 'model/getModelVersions',
        payload: { gid, force },
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
