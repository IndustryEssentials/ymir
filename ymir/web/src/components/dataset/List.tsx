import React, { useEffect, useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import { connect } from 'dva'
import styles from './list.less'
import { Link, useHistory, useLocation } from 'umi'
import { Form, Button, Input, Table, Space, Modal, Row, Col, Tooltip, Pagination, message, Popover } from 'antd'

import t from '@/utils/t'
import { diffTime } from '@/utils/date'
import { getTaskTypeLabel, TASKSTATES, TASKTYPES } from '@/constants/task'
import { ResultStates } from '@/constants/common'
import { canHide, validDataset } from '@/constants/dataset'

import CheckProjectDirty from '@/components/common/CheckProjectDirty'
import EditNameBox from '@/components/form/editNameBox'
import EditDescBox from '@/components/form/editDescBox'
import Terminate from '@/components/task/terminate'
import Hide from '../common/hide'
import RenderProgress from '@/components/common/Progress'
import TypeTag from '@/components/task/TypeTag'
import Actions from '@/components/table/Actions'
import AssetCount from '@/components/dataset/AssetCount'
import Detail from '@/components/project/Detail'
import AddButton from '@/components/dataset/AddButton'

import {
  ScreenIcon,
  TaggingIcon,
  TrainIcon,
  VectorIcon,
  WajueIcon,
  SearchIcon,
  EditIcon,
  CopyIcon,
  StopIcon,
  ArrowDownIcon,
  ArrowRightIcon,
  CompareListIcon,
  DeleteIcon,
} from '@/components/common/Icons'
import { DescPop } from '../common/DescPop'
import useRerunAction from '@/hooks/useRerunAction'

const { useForm } = Form

function Datasets({ pid, project = {}, iterations, groups, ...func }) {
  const location = useLocation()
  const { name } = location.query
  const history = useHistory()
  const [datasets, setDatasets] = useState([])
  const [datasetVersions, setDatasetVersions] = useState({})
  const [total, setTotal] = useState(1)
  const [form] = useForm()
  const [current, setCurrent] = useState({})
  const [visibles, setVisibles] = useState({})
  const [selectedVersions, setSelectedVersions] = useState({ selected: [], versions: {} })
  const hideRef = useRef(null)
  let [lock, setLock] = useState(true)
  const terminateRef = useRef(null)
  const [testingSetIds, setTestingSetIds] = useState([])
  const generateRerun = useRerunAction()
  const [editingDataset, setEditingDataset] = useState({})
  const { datasets: datasetList, versions, query } = useSelector(({ dataset }) => dataset)

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
    const list = setGroupLabelsByProject(datasetList.items, project)
    setDatasets(list)
    setTotal(datasetList.total)
    setTestingSetIds(project?.testingSets || [])
  }, [datasetList, project])

  useEffect(() => {
    Object.keys(visibles).map((key) => {
      if (visibles[key]) {
        fetchVersions(key)
      }
    })
  }, [visibles])

  useEffect(() => {
    const hasDataset = Object.keys(versions).length
    const emptyDataset = Object.values(versions).some((dss) => !dss.length)
    if (hasDataset && emptyDataset) {
      fetchDatasets()
    }
  }, [versions])

  useEffect(() => {
    let dvs = versions
    if (project) {
      dvs = setVersionLabelsByProject(dvs, project)
    }
    if (iterations?.length) {
      dvs = setVersionLabelsByIterations(dvs, iterations)
    }
    setDatasetVersions(dvs)
  }, [project, versions, iterations])

  useEffect(() => {
    Object.keys(versions).forEach((gid) => {
      const vss = versions[gid]
      const needReload = vss.some((ds) => ds.needReload)

      if (needReload) {
        fetchVersions(gid, true)
      }
    })
  }, [versions])

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
        title: showTitle('dataset.column.name'),
        key: 'name',
        dataIndex: 'versionName',
        className: styles[`column_name`],
        render: (name, { id, description, projectLabel, iterationLabel }) => {
          const popContent = <DescPop description={description} style={{ maxWidth: '30vw' }} />
          const content = (
            <Row>
              <Col flex={1}>
                <Link to={`/home/project/${pid}/dataset/${id}`}>{name}</Link>
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
        filters: getRoundFilter(gid),
        onFilter: (round, { iterationRound }) => round === iterationRound,
        ellipsis: true,
      },
      {
        title: showTitle('dataset.column.source'),
        dataIndex: 'taskType',
        render: (type) => <TypeTag type={type} />,
        filters: getTypeFilter(gid),
        onFilter: (type, { taskType }) => type === taskType,
        sorter: (a, b) => a.taskType - b.taskType,
        ellipsis: true,
      },
      {
        title: showTitle('dataset.column.asset_count'),
        dataIndex: 'assetCount',
        render: (num, record) => <AssetCount dataset={record} />,
        sorter: (a, b) => a.assetCount - b.assetCount,
        width: 120,
      },
      {
        title: showTitle('dataset.column.keyword'),
        dataIndex: 'keywords',
        render: (keywords, { state }) => {
          const label = t('dataset.column.keyword.label', {
            keywords: keywords.join(', '),
            total: keywords.length,
          })
          return isValidDataset(state) ? (
            <Tooltip title={label} color="white" overlayInnerStyle={{ color: 'rgba(0,0,0,0.45)', fontSize: 12 }} mouseEnterDelay={0.5}>
              <div>{label}</div>
            </Tooltip>
          ) : null
        },
        ellipsis: {
          showTitle: false,
        },
      },
      {
        title: showTitle('dataset.column.state'),
        dataIndex: 'state',
        render: (state, record) => RenderProgress(state, record),
        // width: 60,
      },
      {
        title: showTitle('dataset.column.create_time'),
        dataIndex: 'createTime',
        sorter: (a, b) => diffTime(a.createTime, b.createTime),
        sortDirections: ['ascend', 'descend', 'ascend'],
        defaultSortOrder: 'descend',
        width: 180,
      },
      {
        title: showTitle('dataset.column.action'),
        key: 'action',
        dataIndex: 'action',
        render: (text, record) => <Actions actions={actionMenus(record)} />,
        className: styles.tab_actions,
        align: 'center',
        width: 300,
      },
    ]
  }

  const actionMenus = (record) => {
    const { id, groupId, state, taskState, task, assetCount } = record
    const invalidDataset = ({ state, assetCount }) => !isValidDataset(state) || assetCount === 0
    const menus = [
      {
        key: 'label',
        label: t('dataset.action.label'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/label?did=${id}`),
        icon: <TaggingIcon />,
      },
      {
        key: 'train',
        label: t('dataset.action.train'),
        hidden: () => invalidDataset(record) || isTestingDataset(id) || !record.keywords.length,
        onclick: () => history.push(`/home/project/${pid}/train?did=${id}`),
        icon: <TrainIcon />,
      },
      {
        key: 'mining',
        label: t('dataset.action.mining'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/mining?did=${id}`),
        icon: <VectorIcon />,
      },
      {
        key: 'preview',
        label: t('common.action.preview'),
        hidden: () => !validDataset(record) || !assetCount,
        onclick: () => history.push(`/home/project/${pid}/dataset/${id}/assets`),
        icon: <SearchIcon className={styles.addBtnIcon} />,
      },
      {
        key: 'merge',
        label: t('common.action.merge'),
        hidden: () => !isValidDataset(state),
        onclick: () => history.push(`/home/project/${pid}/merge?did=${id}`),
        icon: <CompareListIcon className={styles.addBtnIcon} />,
      },
      {
        key: 'filter',
        label: t('common.action.filter'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/filter?did=${id}`),
        icon: <ScreenIcon className={styles.addBtnIcon} />,
      },
      {
        key: 'inference',
        label: t('dataset.action.inference'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/inference?did=${id}`),
        icon: <WajueIcon />,
      },
      {
        key: 'copy',
        label: t('task.action.copy'),
        hidden: () => invalidDataset(record),
        onclick: () => history.push(`/home/project/${pid}/copy?did=${id}`),
        icon: <CopyIcon />,
      },
      {
        key: 'edit',
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
      generateRerun(record),
      {
        key: 'hide',
        label: t('common.action.del'),
        onclick: () => hide(record),
        hidden: () => !canHide(record, project),
        icon: <DeleteIcon />,
      },
    ]
    return menus
  }

  const tableChange = ({ current, pageSize }, filters, sorters = {}) => {}

  const getTypeFilter = (gid) => {
    return getFilters(gid, 'taskType', (type) => t(getTaskTypeLabel(type)))
  }

  const getRoundFilter = (gid) => {
    return getFilters(gid, 'iterationRound', (round) => t('iteration.tag.round', { round }))
  }
  const getFilters = (gid, field, label = () => {}) => {
    const vs = datasetVersions[gid]
    if (vs?.length) {
      const filters = new Set(vs.map((ds) => ds[field]).filter((item) => item))
      return [...filters].map((value) => ({ text: label(value), value }))
    }
  }

  const listChange = (current, pageSize) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    func.updateQuery({ ...query, current, limit, offset })
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

  function setGroupLabelsByProject(datasets, project) {
    return datasets.map((item) => {
      delete item.projectLabel
      item = setLabelByProject(project?.trainSet?.id, 'isTrainSet', item)
      item = setLabelByProject(project?.testSet?.groupId, 'isTestSet', item, project?.testSet?.versionName)
      item = setLabelByProject(project?.miningSet?.groupId, 'isMiningSet', item, project?.miningSet?.versionName)
      return { ...item }
    })
  }

  function setVersionLabelsByProject(versions, project) {
    Object.keys(versions).forEach((gid) => {
      const list = versions[gid]
      const updatedList = list.map((item) => {
        delete item.projectLabel
        const field =
          item.id === project?.testSet?.id ? 'isTestSet' : item.id === project?.miningSet?.id ? 'isMiningSet' : isTestingDataset(item.id) ? 'isTestingSet' : ''
        field && (item = setLabelByProject(item.id, field, item))
        return { ...item }
      })
      versions[gid] = updatedList
    })
    return { ...versions }
  }

  function setVersionLabelsByIterations(versions, iterations) {
    Object.keys(versions).forEach((gid) => {
      const list = versions[gid]
      const updatedList = list.map((item) => {
        delete item.iterationLabel
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
      isTestingSet: 'project.tag.testing',
    }
    item[label] = id && item.id === id
    item.projectLabel = item.projectLabel || (item[label] ? t(maps[label], { version }) : '')
    return item
  }

  function setLabelByIterations(item, iterations) {
    const iteration = iterations.find((iter) =>
      [iter.miningSet, iter.miningResult, iter.labelSet, iter.trainUpdateSet, iter.trainSet].filter((id) => id).includes(item.id),
    )
    if (iteration) {
      item.iterationLabel = t('iteration.tag.round', iteration)
      item.iterationRound = iteration.round
    }
    return item
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

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const saveNameHandle = (result) => {
    if (result) {
      setDatasets((datasets) =>
        datasets.map((dataset) => {
          if (dataset.id === result.id) {
            dataset.name = result.name
          }
          return dataset
        }),
      )
    }
  }

  const saveDescHandle = (result) => {
    if (result) {
      setDatasetVersions((versions) => ({
        ...versions,
        [result.groupId]: versions[result.groupId].map((dataset) => {
          if (dataset.id === result.id) {
            dataset.description = result.description
          }
          return dataset
        }),
      }))
    }
  }

  const editDesc = (dataset) => {
    setEditingDataset({})
    setTimeout(() => setEditingDataset(dataset), 0)
  }

  const add = () => {
    history.push(`/home/project/${pid}/dataset/add`)
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

  const multipleHide = () => {
    const ids = selectedVersions.selected
    const allVss = Object.values(versions).flat()
    const vss = allVss.filter(({ id }) => ids.includes(id))
    hideRef.current.hide(vss, project.hiddenDatasets)
  }

  const hide = (version) => {
    if (project.hiddenDatasets.includes(version.id)) {
      return message.warn(t('dataset.del.single.invalid'))
    }
    hideRef.current.hide([version])
  }

  const hideOk = (result) => {
    result.forEach((item) => fetchVersions(item.dataset_group_id, true))
    fetchDatasets(true)
    setSelectedVersions({ selected: [], versions: {} })
  }

  const multipleInfer = () => {
    const ids = selectedVersions.selected.join('|')
    history.push(`/home/project/${pid}/inference?did=${ids}`)
  }

  const batchMerge = () => {
    const ids = selectedVersions.selected.join(',')
    history.push(`/home/project/${pid}/merge?mid=${ids}`)
  }

  const getDisabledStatus = (filter = () => {}) => {
    const allVss = Object.values(versions).flat()
    const { selected } = selectedVersions
    return !selected.length || allVss.filter(({ id }) => selected.includes(id)).some((version) => filter(version))
  }

  function isValidDataset(state) {
    return ResultStates.VALID === state
  }

  function isRunning(state) {
    return state === ResultStates.READY
  }

  function isTestingDataset(id) {
    return testingSetIds?.includes(id)
  }

  const renderMultipleActions = (
    <>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => isRunning(state))} onClick={multipleHide}>
        <DeleteIcon /> {t('common.action.multiple.del')}
      </Button>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => !isValidDataset(state))} onClick={multipleInfer}>
        <WajueIcon /> {t('common.action.multiple.infer')}
      </Button>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => !isValidDataset(state))} onClick={batchMerge}>
        <WajueIcon /> {t('common.action.multiple.merge')}
      </Button>
    </>
  )

  const renderGroups = (
    <>
      <div className="groupList">
        {datasets.map((group) => (
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
                dataSource={datasetVersions[group.id]}
                onChange={tableChange}
                rowKey={(record) => record.id}
                rowSelection={{
                  selectedRowKeys: selectedVersions.versions[group.id],
                  onChange: (keys) => rowSelectChange(group.id, keys),
                }}
                rowClassName={(record, index) => (index % 2 === 0 ? '' : 'oddRow')}
                columns={columns(group.id)}
                pagination={false}
              />
            </div>
          </div>
        ))}
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
    <div className={styles.dataset}>
      <Detail project={project} />
      <Row className="actions">
        <Col flex={1}>
          <Space>
            <AddButton id={pid} />
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
            initialValues={{ type: query.type, time: query.time, name: name || query.name }}
            onValuesChange={search}
            colon={false}
          >
            <Row>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item name="name" label={t('dataset.query.name')}>
                  <Input placeholder={t('dataset.query.name.placeholder')} style={{ width: '80%' }} allowClear suffix={<SearchIcon />} />
                </Form.Item>
              </Col>
            </Row>
          </Form>
        </div>
        {renderGroups}
      </div>
      <EditDescBox record={editingDataset} handle={saveDescHandle} />
      <EditNameBox record={current} max={80} handle={saveNameHandle} />
      <Hide ref={hideRef} ok={hideOk} />
      <Terminate ref={terminateRef} ok={terminateOk} />
    </div>
  )
}

const props = (state) => {
  return {
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
