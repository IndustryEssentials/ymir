import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import styles from "./list.less"
import { Link, useHistory, useLocation } from "umi"
import { Form, Button, Input, Table, Space, Modal, Row, Col, Tooltip, Pagination, } from "antd"

import t from "@/utils/t"
import { humanize } from "@/utils/number"
import { diffTime } from '@/utils/date'
import { getTaskTypeLabel } from '@/constants/task'
import { states } from '@/constants/dataset'

import StateTag from "@/components/task/stateTag"
import EditBox from "@/components/form/editBox"
import Terminate from "@/components/task/terminate"
import Del from "./del"
import DelGroup from "./delGroup"
import RenderProgress from "@/components/common/progress"
import TypeTag from "@/components/task/typeTag"
import Actions from "@/components/table/actions"

import {
  ImportIcon, ScreenIcon, TaggingIcon, TrainIcon, VectorIcon, WajueIcon, SearchIcon,
  EditIcon, DeleteIcon, CopyIcon, StopIcon, ArrowDownIcon, ArrowRightIcon,
} from "@/components/common/icons"

const { confirm } = Modal
const { useForm } = Form

function Datasets({ pid, project = {}, datasetList, query, versions, ...func }) {
  const location = useLocation()
  const { name } = location.query
  const history = useHistory()
  const [datasets, setDatasets] = useState([])
  const [datasetVersions, setDatasetVersions] = useState({})
  const [iterations, setIterations] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [current, setCurrent] = useState({})
  const [visibles, setVisibles] = useState({})
  const delRef = useRef(null)
  const delGroupRef = useRef(null)
  let [lock, setLock] = useState(true)
  const terminateRef = useRef(null)

  /** use effect must put on the top */
  useEffect(() => {
    if (history.action !== 'POP') {
      initState()
    }
    setLock(false)
  }, [history.location])

  useEffect(() => {
    const list = setGroupLabelsByProject(datasetList.items, project)
    setDatasets(list)
    setTotal(datasetList.total)
  }, [datasetList, project])

  useEffect(() => {
    Object.keys(visibles).map(key => {
      if (visibles[key]) {
        fetchVersions(key)
      }
    })
  }, [visibles])

  useEffect(() => {
    const hasDataset = Object.keys(versions).length
    const emptyDataset = Object.values(versions).some(dss => !dss.length)
    if (hasDataset && emptyDataset) {
      fetchDatasets()
    }
  }, [versions])

  useEffect(() => {
    let dvs = setVersionLabelsByProject(versions, project)
    if (iterations.length) {
      dvs = setVersionLabelsByIterations(versions, iterations)
    }
    setDatasetVersions(dvs)
  }, [versions, project, iterations])

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
      fetchDatasets()
    }
  }, [query, lock])

  useEffect(() => {
    if (location.state?.type) {
      history.replace(location.pathname, {})
    }
  }, [location.state])

  async function initState() {
    await func.resetQuery()
    form.resetFields()
  }

  const columns = (gid) => {
    return [
    {
      title: showTitle("dataset.column.name"),
      key: "name",
      dataIndex: "versionName",
      className: styles[`column_name`],
      render: (name, { id, state, projectLabel, iterationLabel }) => <Row>
        <Col flex={1}><Link to={`/home/project/${pid}/dataset/${id}`}>{name}</Link></Col>
        <Col flex={'50px'}>
          {projectLabel ? <div className={styles.extraTag}>{projectLabel}</div> : null}
          {iterationLabel ? <div className={styles.extraIterTag}>{iterationLabel}</div> : null}
        </Col>
      </Row>,
      filters: getRoundFilter(gid),
      onFilter: (round, { iterationRound }) => round === iterationRound,
      ellipsis: true,
    },
    {
      title: showTitle("dataset.column.source"),
      dataIndex: "taskType",
      render: (type) => <TypeTag type={type} />,
      filters: getTypeFilter(gid),
      onFilter: (type, { taskType }) => type === taskType,
      sorter: (a, b) => a.taskType - b.taskType,
      ellipsis: true,
    },
    {
      title: showTitle("dataset.column.asset_count"),
      dataIndex: "assetCount",
      render: (num) => humanize(num),
      sorter: (a, b) => a.assetCount - b.assetCount,
      width: 120,
    },
    {
      title: showTitle("dataset.column.keyword"),
      dataIndex: "keywords",
      render: (keywords) => {
        const label = t('dataset.column.keyword.label', { keywords: keywords.join(', '), total: keywords.length })
        return <Tooltip title={label}
          color='white' overlayInnerStyle={{ color: 'rgba(0,0,0,0.45)', fontSize: 12 }}
          mouseEnterDelay={0.5}
        ><div>{label}</div></Tooltip>
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
      dataIndex: "createTime",
      sorter: (a, b) => diffTime(a.createTime, b.createTime),
      sortDirections: ['ascend', 'descend', 'ascend'],
      defaultSortOrder: 'descend',
      width: 180,
    },
    {
      title: showTitle("dataset.column.action"),
      key: "action",
      dataIndex: "action",
      render: (text, record) => <Actions menus={actionMenus(record)} />,
      className: styles.tab_actions,
      align: "center",
      width: 300,
    },
  ]}

  const actionMenus = (record) => {
    const { id, name, state, versionName, isProtected } = record
    const menus = [
      {
        key: "fusion",
        label: t("dataset.action.fusion"),
        hidden: () => !isValidDataset(state),
        onclick: () => history.push(`/home/task/fusion/${pid}?did=${id}`),
        icon: <ScreenIcon className={styles.addBtnIcon} />,
      },
      {
        key: "train",
        label: t("dataset.action.train"),
        hidden: () => !isValidDataset(state),
        onclick: () => history.push(`/home/task/train/${pid}?did=${id}`),
        icon: <TrainIcon />,
      },
      {
        key: "mining",
        label: t("dataset.action.mining"),
        hidden: () => !isValidDataset(state),
        onclick: () => history.push(`/home/task/mining/${pid}?did=${id}`),
        icon: <VectorIcon />,
      },
      {
        key: "inference",
        label: t("dataset.action.inference"),
        hidden: () => !isValidDataset(state),
        onclick: () => history.push(`/home/task/inference/${pid}?did=${id}`),
        icon: <WajueIcon />,
      },
      {
        key: "label",
        label: t("dataset.action.label"),
        hidden: () => !isValidDataset(state),
        onclick: () => history.push(`/home/task/label/${pid}?did=${id}`),
        icon: <TaggingIcon />,
      },
      {
        key: "copy",
        label: t("task.action.copy"),
        hidden: () => !isValidDataset(state),
        onclick: () => history.push(`/home/task/copy/${pid}?did=${id}`),
        icon: <CopyIcon />,
      },
      {
        key: "stop",
        label: t("task.action.terminate"),
        onclick: () => stop(record),
        hidden: () => !isRunning(state),
        icon: <StopIcon />,
      },
      // {
      //   key: "del",
      //   label: t("dataset.action.del"),
      //   onclick: () => del(id, `${name} ${versionName}`),
      //   disabled: isProtected,
      //   hidden: () => isRunning(state),
      //   icon: <DeleteIcon />,
      // },
    ]
    return menus
  }

  const tableChange = ({ current, pageSize }, filters, sorters = {}) => {
  }

  const getTypeFilter = gid => {
    return getFilters(gid, 'taskType', (type) => t(getTaskTypeLabel(type)))
  }

  const getRoundFilter = gid => {
    return getFilters(gid, 'iterationRound', (round) => t('iteration.tag.round', { round }))
  }
  const getFilters = (gid, field, label = () => {}) => {
    const vs = datasetVersions[gid]
    if (vs?.length) {
      const filters = new Set(vs.map(ds => ds[field]).filter(item => item))
      return [...filters].map(value => ({ text: label(value), value }))
    }
  }

  const listChange = ({ current, pageSize }) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    func.updateQuery({ ...query, limit, offset })
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  async function fetchDatasets() {
    func.getDatasets(pid, query)
  }

  function showVersions(id) {
    setVisibles((old) => ({ ...old, [id]: !old[id] }))
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

  function setGroupLabelsByProject(datasets, project) {
    return datasets.map(item => {
      item = setLabelByProject(project?.trainSet?.id, 'isTrainSet', item)
      item = setLabelByProject(project?.testSet?.groupId, 'isTestSet', item, project?.testSet?.versionName)
      item = setLabelByProject(project?.miningSet?.groupId, 'isMiningSet', item, project?.miningSet?.versionName)
      return { ...item }
    })
  }

  function setVersionLabelsByProject(versions, project) {
    Object.keys(versions).forEach(gid => {
      const list = versions[gid]
      const updatedList = list.map(item => {
        item = setLabelByProject(project?.testSet?.id, 'isTestSet', item)
        item = setLabelByProject(project?.miningSet?.id, 'isMiningSet', item)
        return { ...item }
      })
      versions[gid] = updatedList
    })
    return { ...versions }
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

  function setLabelByProject(id, label, item, version = '') {
    const maps = {
      isTrainSet: 'project.tag.train',
      isTestSet: 'project.tag.test',
      isMiningSet: 'project.tag.mining',
    }
    item[label] = id && item.id === id
    item.projectLabel = item.projectLabel || (item[label] ? t(maps[label], { version }) : '')
    return item
  }

  function setLabelByIterations(item, iterations) {
    iterations.forEach(iteration => {
      const ids = [
        iteration.miningSet,
        iteration.miningResult,
        iteration.labelSet,
        iteration.trainUpdateSet,
        iteration.trainSet,
      ].filter(id => id)
      if (ids.includes(item.id)) {
        item.iterationLabel = t('iteration.tag.round', iteration)
        item.iterationRound = iteration.round
      }
    })
    return item
  }

  const delGroup = (id, name) => {
    delGroupRef.current.del(id, name)
  }
  const del = (id, name) => {
    delRef.current.del(id, name)
  }

  const delOk = (id) => {
    func.getVersions(id, true)
    fetchDatasets()
  }

  const delGroupOk = () => {
    fetchDatasets()
  }
  
  const stop = (dataset) => {
    terminateRef.current.confirm(dataset)
  }

  function terminateOk({ }, { groupId }) {
    groupId && func.getVersions(groupId, true)
  }

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const saveName = async (record, name) => {
    const result = await func.updateDataset(record.id, name)
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

  const add = () => {
    history.push(`/home/dataset/add/${pid}`)
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


  function isValidDataset(state) {
    return states.VALID === state
  }

  function isRunning(state) {
    return state === states.READY
  }

  const addBtn = (
    <Button type="primary" onClick={add}>
      <ImportIcon /> {t("dataset.import.label")}
    </Button>
  )

  const renderGroups = (<>
    <div className={styles.groupList}>
      {datasets.map(group => <div className={styles.groupItem} key={group.id}>
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
            dataSource={datasetVersions[group.id]}
            onChange={tableChange}
            rowKey={(record) => record.id}
            rowClassName={(record, index) => index % 2 === 0 ? styles.normalRow : styles.oddRow}
            columns={columns(group.id)}
            pagination={false}
          />
        </div>
      </div>)}
    </div>
    <Pagination className={styles.pager} showQuickJumper showSizeChanger total={total} defaultCurrent={1} defaultPageSize={query.limit} onChange={listChange} />
  </>)

  return (
    <div className={styles.dataset}>
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
            initialValues={{ type: query.type, time: query.time, name: name || query.name }}
            onValuesChange={search}
            colon={false}
          >
            <Row>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item name="name" label={t('dataset.query.name')}>
                  <Input placeholder={t("dataset.query.name.placeholder")} style={{ width: '80%' }} allowClear suffix={<SearchIcon />} />
                </Form.Item>
              </Col>
            </Row>

          </Form>
        </div>
        {renderGroups}
      </div>
      <EditBox record={current} max={80} action={saveName}>
        {current.type ? <Form.Item
          label={t('dataset.column.source')}
        >
          <TypeTag type={current.type} id={current.id} name={current.task_name} />
        </Form.Item> : null}
        {current.state ? <Form.Item
          label={t('dataset.column.state')}
        >
          <StateTag mode='text' state={current.state} />
        </Form.Item> : null}
      </EditBox>
      <DelGroup ref={delGroupRef} ok={delGroupOk} />
      <Del ref={delRef} ok={delOk} />
      <Terminate ref={terminateRef} ok={terminateOk} />
    </div>
  )
}

const props = (state) => {
  return {
    logined: state.user.logined,
    datasetList: state.dataset.datasets,
    versions: state.dataset.versions,
    query: state.dataset.query,
  }
}

const actions = (dispatch) => {
  return {
    getDatasets(pid, query) {
      return dispatch({
        type: 'dataset/getDatasetGroups',
        payload: { pid, query },
      })
    },
    getVersions(gid, force = false) {
      return dispatch({
        type: 'dataset/getDatasetVersions',
        payload: { gid, force },
      })
    },
    delDataset(id) {
      return dispatch({
        type: 'dataset/delDataset',
        payload: id,
      })
    },
    updateDataset(id, name) {
      return dispatch({
        type: 'dataset/updateDataset',
        payload: { id, name },
      })
    },
    getIterations(id) {
      return dispatch({
        type: 'iteration/getIterations',
        payload: { id, },
      })
    },
    updateQuery(query) {
      return dispatch({
        type: 'dataset/updateQuery',
        payload: query,
      })
    },
    resetQuery: () => {
      return dispatch({
        type: 'dataset/resetQuery',
      })
    },
  }
}

export default connect(props, actions)(Datasets)
