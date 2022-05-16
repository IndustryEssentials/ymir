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
import { TASKTYPES, TASKSTATES } from '@/constants/task'
import t from "@/utils/t"
import { percent } from '@/utils/number'

import Actions from "@/components/table/actions"
import TypeTag from "@/components/task/typeTag"
import RenderProgress from "@/components/common/progress"
import Terminate from "@/components/task/terminate"
import Hide from "../common/hide"
import EditBox from "@/components/form/editBox"
import { getTensorboardLink } from "@/services/common"

import {
  ShieldIcon, VectorIcon, EditIcon,
  EyeOffIcon, DeleteIcon, FileDownloadIcon, TrainIcon, WajueIcon, StopIcon,SearchIcon,
  ArrowDownIcon, ArrowRightIcon, ImportIcon, BarchartIcon
} from "@/components/common/icons"

const { useForm } = Form

function Model({ pid, project = {}, iterations, group, modelList, versions, query, ...func }) {
  const history = useHistory()
  const { name } = history.location.query
  const [models, setModels] = useState([])
  const [modelVersions, setModelVersions] = useState({})
  const [total, setTotal] = useState(1)
  const [selectedVersions, setSelectedVersions] = useState({})
  const [form] = useForm()
  const [current, setCurrent] = useState({})
  const [visibles, setVisibles] = useState(group ? { [group]: true } : {})
  let [lock, setLock] = useState(true)
  const hideRef = useRef(null)
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
    if (iterations?.length) {
      dvs = setVersionLabelsByIterations(versions, iterations)
    }
    setModelVersions(dvs)
  }, [versions, project, iterations])

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
      render: (type) => <TypeTag type={type} />,
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

  const hideHidden = ({ state, id }) => isRunning(state) || project?.hiddenModels?.includes(id)

  const listChange = (current, pageSize) => {
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
        const iteration = iterations.find(iter => iter.model === item.id)
        if (iteration) {
          item.iterationLabel = t('iteration.tag.round', iteration)
        }
        return { ...item }
      })
      versions[gid] = updatedList
    })
    return { ...versions }
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

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  async function getData() {
    await func.getModels(pid, query)
  }

  const actionMenus = (record) => {
    const { id, name, url, state, taskState, taskType, task, isProtected } = record
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
        hidden: () => taskState === TASKSTATES.PENDING || !isRunning(state) || task.is_terminated,
        icon: <StopIcon />,
      },
      {
        key: "tensor",
        label: 'Tensorboard',
        target: '_blank',
        link: getTensorboardLink(task.hash),
        hidden: () => taskType !== TASKTYPES.TRAINING,
        icon: <BarchartIcon />,
      },
      {
        key: "hide",
        label: t("common.action.hide"),
        onclick: () => hide(record),
        hidden: ()=> hideHidden(record),
        icon: <EyeOffIcon />,
      },
    ]
    return actions
  }

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const multipleInfer = () => {
    const ids = Object.values(selectedVersions)
    history.push(`/home/task/inference/${pid}?mid=${ids}`)
  }

  const multipleHide = () => {
    const ids = Object.values(selectedVersions).flat()
    const allVss = Object.values(versions).flat()
    const vss = allVss.filter(({id}) => ids.includes(id))
    hideRef.current.hide(vss, project.hiddenModels)
  }

  const hide = (version) => {
    if (project.hiddenModels.includes(version.id)) {
      return message.warn(t('dataset.hide.single.invalid'))
    }
    hideRef.current.hide([version])
  }

  const hideOk = (result) => {
    result.forEach(item => fetchVersions(item.model_group_id, true))
    getData()
    setSelectedVersions({})
  }

  
  function rowSelectChange(gid, rowKeys) {
    setSelectedVersions(old => ({ ...old, [gid]: rowKeys }))
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

  const renderMultipleActions = Object.values(selectedVersions).flat().length ? (
    <>
      <Button type="primary" onClick={multipleHide}>
        <EyeOffIcon /> {t("common.action.multiple.hide")}
      </Button>
      <Button type="primary" onClick={multipleInfer}>
        <WajueIcon /> {t("common.action.multiple.infer")}
      </Button>
    </>
  ) : null

  const renderGroups = (<>
    <div className='groupList'>
      {models.length ? models.map(group => <div className={styles.groupItem} key={group.id}>
        <Row className='groupTitle'>
          <Col flex={1} onClick={() => showVersions(group.id)}>
            <span className='foldBtn'>{visibles[group.id] ? <ArrowDownIcon /> : <ArrowRightIcon />} </span>
            <span className='groupName'>{group.name}</span>
            {group.projectLabel ? <span className={styles.extraTag}>{group.projectLabel}</span> : null}
          </Col>
          <Col><Space>
            <a onClick={() => edit(group)} title={t('common.modify')}><EditIcon /></a>
          </Space></Col>
        </Row>
        <div className='groupTable' hidden={!visibles[group.id]}>
          <Table
            dataSource={modelVersions[group.id]}
            onChange={tableChange}
            rowKey={(record) => record.id}
            rowSelection={{
              onChange: (keys) => rowSelectChange(group.id, keys),
              getCheckboxProps: (record) => ({ disabled: isRunning(record.state), }),
            }}
            rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
            columns={columns}
            pagination={false}
          />
        </div>
      </div>) : <Empty />}
    </div>
    <Pagination className={`pager ${styles.pager}`} showQuickJumper showSizeChanger total={total} defaultCurrent={1} defaultPageSize={query.limit} onChange={listChange} />
  </>)

  return (
    <div className={styles.model}>
      <div className='actions'>
        <Space>
          {addBtn}
          {renderMultipleActions}
        </Space>
      </div>
      <div className={`list ${styles.list}`}>
        <div className={`search ${styles.search}`}>
          <Form
            name='queryForm'
            form={form}
            labelCol={{ flex: '120px' }}
            initialValues={{ time: query.time, name: name || query.name }}
            onValuesChange={search}
            colon={false}
          >
            <Row>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item name="name" label={t('model.query.name')}>
                  <Input placeholder={t("model.query.name.placeholder")} style={{ width: '80%' }} allowClear suffix={<SearchIcon />} />
                </Form.Item>
              </Col>
            </Row>
          </Form>
        </div>

        {renderGroups}
      </div>
      <EditBox record={current} max={80} action={saveName}></EditBox>
      <Hide ref={hideRef} type={1} msg='model.action.hide.confirm.content' ok={hideOk} />
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
