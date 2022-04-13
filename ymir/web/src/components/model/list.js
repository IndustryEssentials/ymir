import React, { useEffect, useState, useRef } from "react"
import { connect } from 'dva'
import styles from "./list.less"
import { Link, useHistory } from "umi"
import { Form, Input, Table, Modal, Row, Col, Tooltip, Pagination, Space, Empty, Button, } from "antd"
import {
  SearchOutlined,
} from "@ant-design/icons"

import { diffTime } from '@/utils/date'
import { states } from '@/constants/model'
import t from "@/utils/t"
import { percent } from '@/utils/number'
import { getTimes, getModelImportTypes } from '@/constants/query'

import Actions from "@/components/table/actions"
import TypeTag from "@/components/task/typeTag"
import RenderProgress from "@/components/common/progress"
import Terminate from "@/components/task/terminate"
import Del from "./del"
import DelGroup from "./delGroup"
import EditBox from "@/components/form/editBox"

import { ShieldIcon, VectorIcon, EditIcon,
   DeleteIcon, FileDownloadIcon, TrainIcon, WajueIcon, StopIcon, 
   ArrowDownIcon, ArrowRightIcon, ImportIcon } from "@/components/common/icons"

const { useForm } = Form

function Model({ pid, project = {}, modelList, versions, query, ...func }) {
  const history = useHistory()
  const { name } = history.location.query
  const [models, setModels] = useState([])
  const [modelVersions, setModelVersions] = useState({})
  const [iterations, setIterations] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [current, setCurrent] = useState({})
  const [visibles, setVisibles] = useState({})
  let [lock, setLock] = useState(true)
  const delRef = useRef(null)
  const delGroupRef = useRef(null)
  const terminateRef = useRef(null)

  /** use effect must put on the top */
  useEffect(() => {
    if (history.action !== 'POP') {
      initState()
    }
    setLock(false)
  }, [history.location])

  useEffect(() => {
    const mds = setGroupLabelsByProject(modelList.items, project)
    setModels(mds)
    setTotal(modelList.total)
  }, [modelList, project])

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

  useEffect(() => {
    Object.keys(visibles).map(key => {
      if (visibles[key]) {
        fetchVersions(key)
      }
    })
  }, [visibles])

  useEffect(() => {
    let dvs = setVersionLabelsByProject(versions, project)
    if (iterations.length) {
      dvs = setVersionLabelsByIterations(versions, iterations)
    }
    setModelVersions(dvs)
  }, [versions, project, iterations])

  useEffect(() => {
    pid && fetchIterations(pid)
  }, [pid])

  useEffect(async () => {
    if (name) {
      await func.updateQuery({ ...query, name })
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
    await func.resetQuery()
    form.resetFields()
  }

  const types = getModelImportTypes()

  const times = getTimes()

  const columns = [
    {
      title: showTitle("model.column.name"),
      dataIndex: "versionName",
      className: styles[`column_name`],
      render: (name, { id, state, projectLabel, iterationLabel }) => <Row>
        <Col flex={1}><Link to={`/home/project/${pid}/model/${id}`}>{name}</Link></Col>
        <Col flex={'50px'}>
          {projectLabel ? <div className={styles.extraTag}>{projectLabel}</div> : null}
          {iterationLabel ? <div className={styles.extraIterTag}>{iterationLabel}</div> : null}
        </Col>
      </Row>,
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
      sorter: (a, b) => a - b,
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
      sorter: (a, b) => diffTime(a.createTime, b.createTime),
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
    func.updateQuery({ ...query, limit, offset })
  }


  async function showVersions(id) {
    setVisibles((old) => ({ ...old, [id]: !old[id] }))
  }


  function setVersionLabelsByIterations(versions, iterations) {
    Object.keys(versions).forEach(gid => {
      const list = versions[gid]
      const updatedList = list.map(item => {
        item = setLabelByIterations(item, iterations)
        return { ...item }
      })
      versions[gid] = updatedList
    })
    return { ...versions }
  }

  function setLabelByIterations(item, iterations) {
    iterations.forEach(iteration => {
      if (iteration.model && iteration.model === item.id) {
        item.iterationLabel = t('iteration.tag.round', iteration)
      }
    })
    return item
  }

  function setVersionLabelsByProject(versions, project) {
    Object.keys(versions).forEach(gid => {
      const list = versions[gid]
      const updatedList = list.map(item => {
        item = setLabelByProject(project?.model, 'isInitModel', item)
        return { ...item }
      })
      versions[gid] = updatedList
    })
    return { ...versions }
  }

  function setGroupLabelsByProject(items, project) {
    return items.map(item => {
      item = setLabelByProject(project?.model, 'isInitModel', item)
      return { ...item }
    })
  }

  function setLabelByProject(id, label, item, version = '') {
    const maps = {
      isInitModel: 'project.tag.model',
    }
    item[label] = id && item.id === id
    item.projectLabel = item.projectLabel || (item[label] ? t(maps[label], { version }) : '')
    return item
  }

  async function fetchVersions(id, force) {
    await func.getVersions(id, force)
  }

  async function fetchIterations(pid) {
    const iterations = await func.getIterations(pid)
    if (iterations) {
      setIterations(iterations)
    }
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  async function getData() {
    await func.getModels(pid, query)
  }

  const actionMenus = (record) => {
    const { id, name, url, state, versionName, isProtected } = record
    const actions = [
      {
        key: "verify",
        label: t("model.action.verify"),
        hidden: () => !isValidModel(state),
        onclick: () => history.push(`/home/project/${pid}/model/${id}/verify`),
        icon: <ShieldIcon />,
      },
      {
        key: "download",
        label: t("model.action.download"),
        link: url,
        target: '_blank',
        hidden: () => !isValidModel(state),
        icon: <FileDownloadIcon />,
      },
      {
        key: "mining",
        label: t("dataset.action.mining"),
        hidden: () => !isValidModel(state),
        onclick: () => history.push(`/home/task/mining/${pid}?mid=${id}`),
        icon: <VectorIcon />,
      },
      {
        key: "train",
        label: t("dataset.action.train"),
        hidden: () => !isValidModel(state),
        onclick: () => history.push(`/home/task/train/${pid}?mid=${id}`),
        icon: <TrainIcon />,
      },
      {
        key: "inference",
        label: t("dataset.action.inference"),
        hidden: () => !isValidModel(state),
        onclick: () => history.push(`/home/task/inference/${pid}?mid=${id}`),
        icon: <WajueIcon />,
      },
      {
        key: "stop",
        label: t("task.action.terminate"),
        onclick: () => stop(record),
        hidden: () => !isRunning(state),
        icon: <StopIcon />,
      },
    ]
    // const delAction = {
    //   key: "del",
    //   label: t("dataset.action.del"),
    //   onclick: () => del(id, `${name} ${versionName}`),
    //   className: styles.action_del,
    //   disabled: isProtected,
    //   icon: <DeleteIcon />,
    // }
    return actions
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
    func.getVersions(id, true)
  }

  const delGroupOk = () => {
    getData()
  }

  const stop = (dataset) => {
    terminateRef.current.confirm(dataset)
  }

  function terminateOk({ }, { groupId }) {
    groupId && func.getVersions(groupId, true)
  }

  const saveName = async (record, name) => {
    const result = await func.updateModel(record.id, name)
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
      func.updateQuery({ ...query, ...values, })
    } else {
      setTimeout(() => {
        if (name === form.getFieldValue('name')) {
          func.updateQuery({ ...query, name, })
        }
      }, 1000)
    }
  }

  function isValidModel(state) {
    return states.VALID === state
  }

  function isRunning(state) {
    return states.READY === state
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
          <Col flex={1} onClick={() => showVersions(group.id)}>
            <span className={styles.foldBtn}>{visibles[group.id] ? <ArrowDownIcon /> : <ArrowRightIcon />} </span>
            <span className={styles.groupName}>{group.name}</span>
            {group.projectLabel ? <span className={styles.extraTag}>{group.projectLabel}</span> : null}
          </Col>
          <Col><Space>
            <a onClick={() => edit(group)} title={t('common.modify')}><EditIcon /></a>
            <a hidden={true} onClick={() => delGroup(group.id, group.name)} title={t('common.del')}><DeleteIcon /></a>
          </Space></Col>
        </Row>
        <div className={styles.groupTable} hidden={!visibles[group.id]}>
          <Table
            dataSource={modelVersions[group.id]}
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
      <Terminate ref={terminateRef} ok={terminateOk} />
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
    getIterations(id) {
      return dispatch({
        type: 'iteration/getIterations',
        payload: { id, },
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
