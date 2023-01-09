import React, { useEffect, useState, useRef } from 'react'
import { connect } from 'dva'
import styles from './list.less'
import { Link, useHistory, useSelector } from 'umi'
import { Form, Input, Table, Modal, Row, Col, Tooltip, Pagination, Space, Empty, Button, message, Popover } from 'antd'

import { diffTime } from '@/utils/date'
import { ResultStates } from '@/constants/common'
import { TASKTYPES, TASKSTATES } from '@/constants/task'
import t from '@/utils/t'
import usePublish from '@/hooks/usePublish'
import { getDeployUrl } from '@/constants/common'

import CheckProjectDirty from '@/components/common/CheckProjectDirty'
import Actions from '@/components/table/Actions'
import TypeTag from '@/components/task/TypeTag'
import RenderProgress from '@/components/common/Progress'
import Terminate from '@/components/task/terminate'
import Hide from '../common/hide'
import EditNameBox from '@/components/form/editNameBox'
import EditDescBox from '@/components/form/editDescBox'
import { getTensorboardLink } from '@/constants/common'

import {
  ShieldIcon,
  VectorIcon,
  EditIcon,
  EyeOffIcon,
  DeleteIcon,
  FileDownloadIcon,
  TrainIcon,
  WajueIcon,
  StopIcon,
  SearchIcon,
  ArrowDownIcon,
  ArrowRightIcon,
  ImportIcon,
  BarchartIcon,
} from '@/components/common/Icons'
import EditStageCell from './editStageCell'
import { DescPop } from '../common/DescPop'
import useRerunAction from '../../hooks/useRerunAction'

const { useForm } = Form

function Model({ pid, project = {}, iterations, groups, versions, query, ...func }) {
  const history = useHistory()
  const { name } = history.location.query
  const [models, setModels] = useState([])
  const [modelVersions, setModelVersions] = useState({})
  const [total, setTotal] = useState(1)
  const [selectedVersions, setSelectedVersions] = useState({ selected: [], versions: {} })
  const [form] = useForm()
  const [current, setCurrent] = useState({})
  const [visibles, setVisibles] = useState({})
  const [trainingUrl, setTrainingUrl] = useState('')
  let [lock, setLock] = useState(true)
  const hideRef = useRef(null)
  const delGroupRef = useRef(null)
  const terminateRef = useRef(null)
  const generateRerun = useRerunAction()
  const [publish, publishResult] = usePublish()
  const [editingModel, setEditingModel] = useState({})
  const modelList = useSelector(({ model }) => model.models[pid] || { items: [], total: 0 })

  /** use effect must put on the top */
  useEffect(() => {
    if (history.action !== 'POP') {
      initState()
    }
    setLock(false)
  }, [history.location])

  useEffect(() => {
    const initVisibles = groups.reduce((prev, group) => ({ ...prev, [group]: true }), {})
    setVisibles(initVisibles)
  }, [groups])

  useEffect(() => {
    const mds = setGroupLabelsByProject(modelList.items, project)
    setModels(mds)
    setTotal(modelList.total)
  }, [modelList, project])

  useEffect(() => {
    const hasModel = Object.keys(versions).length
    const emptyModel = Object.values(versions).some((models) => !models.length)
    if (hasModel && emptyModel) {
      getData()
    }
  }, [versions])

  useEffect(() => {
    Object.keys(versions).forEach((gid) => {
      const vss = versions[gid]
      const needReload = vss.some((ds) => ds.needReload)
      if (needReload) {
        fetchVersions(gid, true)
      }
    })
  }, [versions])

  useEffect(() => {
    Object.keys(visibles).map((key) => {
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

  useEffect(() => {
    const selected = selectedVersions.selected
    const mvs = Object.values(modelVersions)
      .flat()
      .filter((version) => selected.includes(version.id))
    const hashs = mvs.map((version) => version.task.hash)
    const url = getTensorboardLink(hashs)
    setTrainingUrl(url)
  }, [selectedVersions])

  async function initState() {
    await func.resetQuery()
    form.resetFields()
  }

  const columns = [
    {
      title: showTitle('model.column.name'),
      dataIndex: 'versionName',
      className: styles[`column_name`],
      render: (name, { id, description, projectLabel, iterationLabel }) => {
        const popContent = <DescPop description={description} style={{ maxWidth: '30vw' }} />
        const content = (
          <Row>
            <Col flex={1}>
              <Link to={`/home/project/${pid}/model/${id}`}>{name}</Link>
            </Col>
            <Col flex={'50px'}>
              {projectLabel ? <div className={styles.extraTag}>{projectLabel}</div> : null}
              {iterationLabel ? <div className={styles.extraIterTag}>{iterationLabel}</div> : null}
            </Col>
          </Row>
        )
        return description ? (
          <Popover title={t('common.desc')} content={popContent}>
            {content}
          </Popover>
        ) : (
          content
        )
      },
      ellipsis: true,
    },
    {
      title: showTitle('model.column.source'),
      dataIndex: 'taskType',
      render: (type) => <TypeTag type={type} />,
    },
    {
      title: showTitle('model.column.stage'),
      dataIndex: 'recommendStage',
      render: (_, record) => (isValidModel(record.state) ? <EditStageCell record={record} saveHandle={updateModelVersion} /> : null),
      // align: 'center',
      width: 300,
    },
    {
      title: showTitle('dataset.column.state'),
      dataIndex: 'state',
      render: (state, record) => RenderProgress(state, record),
      // width: 60,
    },
    {
      title: showTitle('model.column.create_time'),
      dataIndex: 'createTime',
      sorter: (a, b) => diffTime(a.createTime, b.createTime),
      width: 200,
      align: 'center',
    },
    {
      title: showTitle('model.column.action'),
      key: 'action',
      dataIndex: 'action',
      render: (text, record) => <Actions actions={actionMenus(record)} showCount={4} />,
      className: styles.tab_actions,
      align: 'center',
      width: '280px',
    },
  ]

  const tableChange = ({ current, pageSize }, filters, sorters = {}) => {}

  const hideHidden = ({ state, id }) => isRunning(state) || project?.hiddenModels?.includes(id)

  const listChange = (current, pageSize) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    func.updateQuery({ ...query, current, limit, offset })
  }

  function updateModelVersion(result) {
    setModelVersions((mvs) => {
      return {
        ...mvs,
        [result.groupId]: mvs[result.groupId].map((version) => {
          return version.id === result.id ? result : version
        }),
      }
    })
  }

  async function showVersions(id) {
    setVisibles((old) => ({ ...old, [id]: !old[id] }))
  }

  function setVersionLabelsByIterations(versions, iterations) {
    Object.keys(versions).forEach((gid) => {
      const list = versions[gid]
      const updatedList = list.map((item) => {
        delete item.iterationLabel
        const iteration = iterations.find((iter) => iter.model === item.id)
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
    Object.keys(versions).forEach((gid) => {
      const list = versions[gid]
      const updatedList = list.map((item) => {
        delete item.projectLabel
        item = setLabelByProject(project?.model, 'isInitModel', item)
        return { ...item }
      })
      versions[gid] = updatedList
    })
    return { ...versions }
  }

  function setGroupLabelsByProject(items, project) {
    return items.map((item) => {
      delete item.projectLabel
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
    const { id, name, url, state, taskState, taskType, task, isProtected, stages, recommendStage } = record

    const actions = [
      {
        key: 'publish',
        label: t('model.action.publish'),
        hidden: () => !isValidModel(state) || !getDeployUrl(),
        onclick: () => publish(record),
        icon: <ShieldIcon />,
      },
      {
        key: 'verify',
        label: t('model.action.verify'),
        hidden: () => !isValidModel(state),
        onclick: () => history.push(`/home/project/${pid}/model/${id}/verify`),
        icon: <ShieldIcon />,
      },
      {
        key: 'download',
        label: t('model.action.download'),
        link: url,
        target: '_blank',
        hidden: () => !isValidModel(state),
        icon: <FileDownloadIcon />,
      },
      {
        key: 'mining',
        label: t('dataset.action.mining'),
        hidden: () => !isValidModel(state),
        onclick: () => history.push(`/home/project/${pid}/mining?mid=${id},${recommendStage}`),
        icon: <VectorIcon />,
      },
      {
        key: 'train',
        label: t('dataset.action.train'),
        hidden: () => !isValidModel(state),
        onclick: () => history.push(`/home/project/${pid}/train?mid=${id},${recommendStage}`),
        icon: <TrainIcon />,
      },
      {
        key: 'inference',
        label: t('dataset.action.inference'),
        hidden: () => !isValidModel(state),
        onclick: () => history.push(`/home/project/${pid}/inference?mid=${id},${recommendStage}`),
        icon: <WajueIcon />,
      },
      {
        key: 'edit.desc',
        label: t('common.action.edit.desc'),
        onclick: () => editDesc(record),
        icon: <EditIcon />,
      },
      {
        key: 'stop',
        label: t('task.action.terminate'),
        onclick: () => stop(record),
        hidden: () => taskState === TASKSTATES.PENDING || !isRunning(state) || task.is_terminated,
        icon: <StopIcon />,
      },
      {
        key: 'tensor',
        label: t('task.action.training'),
        target: '_blank',
        link: getTensorboardLink(task.hash),
        hidden: () => taskType !== TASKTYPES.TRAINING,
        icon: <BarchartIcon />,
      },
      generateRerun(record),
      {
        key: 'hide',
        label: t('common.action.hide'),
        onclick: () => hide(record),
        hidden: () => hideHidden(record),
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
    const { selected } = selectedVersions
    const versionsObject = Object.values(versions).flat()
    const stages = versionsObject
      .filter((md) => selected.includes(md.id))
      .map((md) => {
        return [md.id, md.recommendStage].toString()
      })
    if (stages.length) {
      history.push(`/home/project/${pid}/inference?mid=${stages.join('|')}`)
    } else {
      message.warning(t('model.list.batch.invalid'))
    }
  }

  const multipleHide = () => {
    const allVss = Object.values(versions).flat()
    const vss = allVss.filter(({ id, state }) => selectedVersions.selected.includes(id))
    if (vss.length) {
      hideRef.current.hide(vss, project.hiddenModels)
    } else {
      message.warning(t('model.list.batch.invalid'))
    }
  }

  const getDisabledStatus = (filter = () => {}) => {
    const allVss = Object.values(versions).flat()
    const { selected } = selectedVersions
    return !selected.length || allVss.filter(({ id }) => selected.includes(id)).some((version) => filter(version))
  }

  const hide = (version) => {
    if (project.hiddenModels.includes(version.id)) {
      return message.warn(t('dataset.hide.single.invalid'))
    }
    hideRef.current.hide([version])
  }

  const hideOk = (result) => {
    result.forEach((item) => fetchVersions(item.model_group_id, true))
    getData()
    setSelectedVersions({ selected: [], versions: {} })
  }

  function rowSelectChange(gid, rowKeys) {
    setSelectedVersions(({ versions }) => {
      versions[gid] = rowKeys
      return {
        selected: Object.values(versions).flat(),
        versions: { ...versions },
      }
    })
  }

  const stop = (dataset) => {
    terminateRef.current.confirm(dataset)
  }

  function terminateOk({}, { groupId }) {
    groupId && func.getVersions(groupId, true)
  }

  const saveNameHandle = (result) => {
    if (result) {
      setModels((models) =>
        models.map((model) => {
          if (model.id === result.id) {
            model.name = result.name
          }
          return model
        }),
      )
    }
  }
  const saveDescHandle = (result) => {
    if (result) {
      setModelVersions((models) => ({
        ...models,
        [result.groupId]: models[result.groupId].map((model) => {
          if (model.id === result.id) {
            model.description = result.description
          }
          return model
        }),
      }))
    }
  }

  const editDesc = (model) => {
    setEditingModel({})
    setTimeout(() => setEditingModel(model), 0)
  }

  const search = (values) => {
    const name = values.name
    if (typeof name === 'undefined') {
      func.updateQuery({ ...query, ...values })
    } else {
      setTimeout(() => {
        if (name === form.getFieldValue('name')) {
          func.updateQuery({ ...query, name })
        }
      }, 1000)
    }
  }

  function isValidModel(state) {
    return ResultStates.VALID === state
  }

  function isRunning(state) {
    return ResultStates.READY === state
  }

  function add() {
    history.push(`/home/project/${pid}/model/import`)
  }

  const addBtn = (
    <Button type="primary" onClick={add}>
      <ImportIcon /> {t('model.import.label')}
    </Button>
  )

  const renderMultipleActions = (
    <>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => isRunning(state))} onClick={multipleHide}>
        <EyeOffIcon /> {t('common.action.multiple.hide')}
      </Button>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => !isValidModel(state))} onClick={multipleInfer}>
        <WajueIcon /> {t('common.action.multiple.infer')}
      </Button>
      <a href={trainingUrl} target="_blank">
        <Button type="primary" disabled={getDisabledStatus()}>
          <BarchartIcon /> {t('task.action.training.batch')}
        </Button>
      </a>
    </>
  )

  const renderGroups = (
    <>
      <div className="groupList">
        {models.length ? (
          models.map((group) => (
            <div className={styles.groupItem} key={group.id}>
              <Row className="groupTitle">
                <Col flex={1} onClick={() => showVersions(group.id)}>
                  <span className="foldBtn">{visibles[group.id] ? <ArrowDownIcon /> : <ArrowRightIcon />} </span>
                  <span className="groupName">{group.name}</span>
                  {group.projectLabel ? <span className={styles.extraTag}>{group.projectLabel}</span> : null}
                </Col>
                <Col>
                  <Space>
                    <a onClick={() => edit(group)} title={t('common.modify')}>
                      <EditIcon />
                    </a>
                  </Space>
                </Col>
              </Row>
              <div className="groupTable" hidden={!visibles[group.id]}>
                <Table
                  dataSource={modelVersions[group.id]}
                  onChange={tableChange}
                  rowKey={(record) => record.id}
                  rowSelection={{
                    selectedRowKeys: selectedVersions.versions[group.id],
                    onChange: (keys) => rowSelectChange(group.id, keys),
                  }}
                  rowClassName={(record, index) => (index % 2 === 0 ? '' : 'oddRow')}
                  columns={columns}
                  pagination={false}
                />
              </div>
            </div>
          ))
        ) : (
          <Empty />
        )}
      </div>
      <Pagination
        className={`pager ${styles.pager}`}
        showQuickJumper
        showSizeChanger
        total={total}
        current={query.current}
        pageSize={query.limit}
        onChange={listChange}
      />
    </>
  )

  return (
    <div className={styles.model}>
      <Row className="actions">
        <Col flex={1}>
          <Space>
            {addBtn}
            {renderMultipleActions}
          </Space>
        </Col>
        <Col>
          <CheckProjectDirty pid={pid} />
        </Col>
      </Row>
      <div className={`list ${styles.list}`}>
        <div className={`search ${styles.search}`}>
          <Form
            name="queryForm"
            form={form}
            labelCol={{ flex: '120px' }}
            initialValues={{ time: query.time, name: name || query.name }}
            onValuesChange={search}
            colon={false}
          >
            <Row>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item name="name" label={t('model.query.name')}>
                  <Input placeholder={t('model.query.name.placeholder')} style={{ width: '80%' }} allowClear suffix={<SearchIcon />} />
                </Form.Item>
              </Col>
            </Row>
          </Form>
        </div>

        {renderGroups}
      </div>
      <EditNameBox type="model" record={current} max={80} handle={saveNameHandle} />
      <EditDescBox type="model" record={editingModel} handle={saveDescHandle} />
      <Hide ref={hideRef} type={1} msg="model.action.hide.confirm.content" ok={hideOk} />
      <Terminate ref={terminateRef} ok={terminateOk} />
    </div>
  )
}

const props = (state) => {
  return {
    logined: state.user.logined,
    query: state.model.query,
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
