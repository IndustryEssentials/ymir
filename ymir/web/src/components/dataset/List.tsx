import React, { FC, useEffect, useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import styles from './list.less'
import { Link, Location, useHistory, useLocation } from 'umi'
import { Form, Button, Input, Table, Space, Modal, Row, Col, Tooltip, Pagination, message, Popover, TableColumnsType } from 'antd'

import t from '@/utils/t'
import { diffTime } from '@/utils/date'
import { getTaskTypeLabel, TASKSTATES, TASKTYPES } from '@/constants/task'
import { readyState, ResultStates, validState } from '@/constants/common'
import { canHide, validDataset } from '@/constants/dataset'

import CheckProjectDirty from '@/components/common/CheckProjectDirty'
import EditNameBox from '@/components/form/editNameBox'
import EditDescBox from '@/components/form/editDescBox'
import Terminate, { RefProps as TRefProps } from '@/components/task/terminate'
import Hide, { RefProps } from '../common/hide'
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
import useRequest from '@/hooks/useRequest'
import StrongTitle from '../table/columns/StrongTitle'

type IsType = {
  isTrainSet?: boolean
  isTestSet?: boolean
  isMiningSet?: boolean
  isTestingSet?: boolean
}
type ExtraLabel = {
  projectLabel?: string
  iterationLabel?: string
  iterationRound?: number
}
type Dataset = YModels.Dataset & ExtraLabel & IsType
type DatasetGroup = YModels.DatasetGroup & ExtraLabel & IsType
type VersionsType = YStates.IdMap<Dataset[]>

type Props = {
  pid: number
  project?: YModels.Project
  groups?: number[]
  iterations?: YModels.Iteration[]
}

const { useForm } = Form

const Datasets: FC<Props> = ({ pid, project, iterations, groups }) => {
  const location: Location<{ type: string}> = useLocation()
  const { name } = location.query as { name?: string }
  const history = useHistory()
  const [datasets, setDatasets] = useState<DatasetGroup[]>([])
  const [datasetVersions, setDatasetVersions] = useState<VersionsType>({})
  const [total, setTotal] = useState(1)
  const [form] = useForm()
  const [current, setCurrent] = useState<DatasetGroup>()
  const [visibles, setVisibles] = useState<{ [key: number]: boolean }>({})
  const [selectedVersions, setSelectedVersions] = useState<{ selected: number[]; versions: { [gid: number]: number[] } }>({
    selected: [],
    versions: {},
  })
  const hideRef = useRef<RefProps>(null)
  let [lock, setLock] = useState(true)
  const terminateRef = useRef<TRefProps>(null)
  const [testingSetIds, setTestingSetIds] = useState<number[]>([])
  const generateRerun = useRerunAction()
  const [editingDataset, setEditingDataset] = useState<Dataset>()
  const { datasets: datasetList, versions, query } = useSelector<YStates.Root, YStates.DatasetState>(({ dataset }) => dataset)

  const { run: getDatasets } = useRequest<YStates.List<YModels.DatasetGroup>>('dataset/getDatasetGroups')
  const { run: getVersions } = useRequest<YStates.List<YModels.Dataset>, [{ gid: number, force?: boolean}]>('dataset/getDatasetVersions')
  const { run: updateQuery } = useRequest('dataset/updateQuery')
  const { run: resetQuery } = useRequest('dataset/resetQuery')

  useEffect(() => {
    if (history.action !== 'POP') {
      initState()
    }
    setLock(false)
  }, [history.location])

  useEffect(() => {
    const initVisibles = groups?.reduce((prev, group) => ({ ...prev, [group]: true }), {})
    setVisibles(initVisibles || {})
  }, [groups])

  useEffect(() => {
    const list = setGroupLabelsByProject(datasetList.items, project)
    setDatasets(list)
    setTotal(datasetList.total)
    setTestingSetIds(project?.testingSets || [])
  }, [datasetList, project])

  useEffect(() => {
    Object.keys(visibles).map((key) => {
      const k = Number(key)
      if (visibles[k]) {
        fetchVersions(k)
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
        fetchVersions(Number(gid), true)
      }
    })
  }, [versions])

  useEffect(() => {
    if (name) {
      updateQuery({ ...query, name })
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

  function initState() {
    resetQuery()
    form.resetFields()
  }

  const columns = (gid: number): TableColumnsType<Dataset> => {
    return [
      {
        title: <StrongTitle label="dataset.column.name" />,
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
        title: <StrongTitle label="dataset.column.source" />,
        dataIndex: 'taskType',
        render: (type) => <TypeTag type={type} />,
        filters: getTypeFilter(gid),
        onFilter: (type, { taskType }) => type === taskType,
        sorter: (a, b) => a.taskType - b.taskType,
        ellipsis: true,
      },
      {
        title: <StrongTitle label="dataset.column.asset_count" />,
        dataIndex: 'assetCount',
        render: (num, record) => <AssetCount dataset={record} />,
        sorter: (a, b) => a.assetCount - b.assetCount,
        width: 120,
      },
      {
        title: <StrongTitle label="dataset.column.keyword" />,
        dataIndex: 'keywords',
        render: (keywords, { state }) => {
          const label = t('dataset.column.keyword.label', {
            keywords: keywords.join(', '),
            total: keywords.length,
          })
          return validState(state) ? (
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
        title: <StrongTitle label="dataset.column.state" />,
        dataIndex: 'state',
        render: (state, record) => RenderProgress(state, record),
        // width: 60,
      },
      {
        title: <StrongTitle label="dataset.column.create_time" />,
        dataIndex: 'createTime',
        sorter: (a, b) => diffTime(a.createTime, b.createTime),
        sortDirections: ['ascend', 'descend', 'ascend'],
        defaultSortOrder: 'descend',
        width: 180,
      },
      {
        title: <StrongTitle label="dataset.column.action" />,
        key: 'action',
        dataIndex: 'action',
        render: (text, record) => <Actions actions={actionMenus(record)} />,
        className: styles.tab_actions,
        align: 'center',
        width: 300,
      },
    ]
  }

  const actionMenus = (record: Dataset): YComponents.Action[] => {
    const { id, groupId, state, taskState, task, assetCount } = record
    const invalidDataset = ({ state, assetCount }: Dataset) => !validState(state) || assetCount === 0
    return [
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
        hidden: () => !validState(state),
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
        hidden: () => taskState === TASKSTATES.PENDING || !readyState(state) || task.is_terminated,
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
  }

  // const tableChange = ({ current, pageSize }, filters, sorters = {}) => {}

  const getTypeFilter = (gid: number) => {
    return getFilters(gid, 'taskType', (type) => (type ? t(getTaskTypeLabel(type as TASKTYPES)) : ''))
  }

  const getRoundFilter = (gid: number) => {
    return getFilters(gid, 'iterationRound', (round) => t('iteration.tag.round', { round }))
  }
  const getFilters = (gid: number, field: 'taskType' | 'iterationRound', label: (round: Dataset[typeof field]) => string) => {
    const vs = datasetVersions[gid]
    if (vs?.length) {
      const filters = [...new Set(vs.map((ds) => ds[field]).filter<number>((item: number | undefined): item is number => !!item))]
      return [...filters].map((value) => ({ text: label(value), value }))
    }
  }

  const listChange = (current: number, pageSize: number) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    updateQuery({ ...query, current, limit, offset })
  }

  function fetchDatasets() {
    getDatasets({ pid, query })
  }

  function showVersions(id: number) {
    setVisibles((old) => ({ ...old, [id]: !old[id] }))
  }

  function fetchVersions(gid: number, force?: boolean) {
    getVersions({ gid, force })
  }

  function setGroupLabelsByProject(datasets: DatasetGroup[], project?: YModels.Project) {
    return datasets.map((item) => {
      delete item.projectLabel
      item = project?.trainSet?.id ? setLabelByProject<DatasetGroup>(project.trainSet.id, 'isTrainSet', item) : item
      item = project?.testSet?.groupId ? setLabelByProject<DatasetGroup>(project.testSet?.groupId, 'isTestSet', item, project?.testSet?.versionName) : item
      item = project?.miningSet?.groupId
        ? setLabelByProject<DatasetGroup>(project.miningSet?.groupId, 'isMiningSet', item, project?.miningSet?.versionName)
        : item
      return { ...item }
    })
  }

  function setVersionLabelsByProject(versions: VersionsType, project: YModels.Project) {
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

  function setVersionLabelsByIterations(versions: VersionsType, iterations: YModels.Iteration[]) {
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

  function setLabelByProject<T extends Dataset | DatasetGroup = Dataset>(id: number, label: keyof IsType, item: T, version = ''): T {
    const maps = {
      isTrainSet: 'project.tag.train',
      isTestSet: 'project.tag.test',
      isMiningSet: 'project.tag.mining',
      isTestingSet: 'project.tag.testing',
    }
    item[label] = !!id && item.id === id
    item.projectLabel = item.projectLabel || (item[label] ? t(maps[label], { version }) : '')
    return item
  }

  function setLabelByIterations(item: Dataset, iterations: YModels.Iteration[]) {
    const iteration = iterations.find((iter) =>
      iter.steps
        .map(({ resultId }) => resultId)
        .filter((id) => id)
        .includes(item.id),
    )
    if (iteration) {
      item.iterationLabel = t('iteration.tag.round', iteration)
      item.iterationRound = iteration.round
    }
    return item
  }

  function rowSelectChange(gid: number, rowKeys: number[]) {
    setSelectedVersions(({ versions }) => {
      versions[gid] = rowKeys
      return {
        selected: Object.values(versions).flat(),
        versions: { ...versions },
      }
    })
  }

  const stop = (dataset: Dataset) => {
    terminateRef.current?.confirm(dataset)
  }

  function terminateOk(t: YModels.Task, ds: YModels.Result) {
    ds?.groupId && fetchVersions(ds.groupId, true)
  }

  const edit = (record: DatasetGroup) => {
    setCurrent(undefined)
    setTimeout(() => setCurrent(record), 0)
  }

  const saveNameHandle = (result: Dataset) => {
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

  const saveDescHandle = (result: Dataset) => {
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

  const editDesc = (dataset: Dataset) => {
    setEditingDataset(undefined)
    setTimeout(() => setEditingDataset(dataset), 0)
  }

  const add = () => {
    history.push(`/home/project/${pid}/dataset/add`)
  }

  const search = (values: { [key: string]: any }) => {
    const name = values.name
    if (typeof name === 'undefined') {
      updateQuery({ ...query, ...values })
    } else {
      setTimeout(() => {
        if (name === form.getFieldValue('name')) {
          updateQuery({ ...query, name })
        }
      }, 1000)
    }
  }

  const multipleHide = () => {
    const ids = selectedVersions.selected
    const allVss = Object.values(versions).flat()
    const vss = allVss.filter(({ id }) => ids.includes(id))
    hideRef.current?.hide(vss, project?.hiddenDatasets)
  }

  const hide = (version: Dataset) => {
    if (project?.hiddenDatasets.includes(version.id)) {
      return message.warn(t('dataset.del.single.invalid'))
    }
    hideRef.current?.hide([version])
  }

  const hideOk = (result: YModels.Result[]) => {
    result.forEach((item) => item?.groupId && fetchVersions(item?.groupId, true))
    fetchDatasets()
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

  const getDisabledStatus = (filter: (ds: Dataset) => boolean) => {
    const allVss = Object.values(versions).flat()
    const { selected } = selectedVersions
    return !selected.length || allVss.filter(({ id }) => selected.includes(id)).some(filter)
  }

  function isTestingDataset(id: number) {
    return testingSetIds?.includes(id)
  }

  const renderMultipleActions = (
    <>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => readyState(state))} onClick={multipleHide}>
        <DeleteIcon /> {t('common.action.multiple.del')}
      </Button>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => !validState(state))} onClick={multipleInfer}>
        <WajueIcon /> {t('common.action.multiple.infer')}
      </Button>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => !validState(state))} onClick={batchMerge}>
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
                // onChange={tableChange}
                rowKey={(record) => record.id}
                rowSelection={{
                  selectedRowKeys: selectedVersions.versions[group.id],
                  onChange: (keys) => rowSelectChange(group.id, keys as number[]),
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
      {editingDataset ? <EditDescBox record={editingDataset} handle={saveDescHandle} /> : null}
      {current ? <EditNameBox record={current} max={80} handle={saveNameHandle} /> : null}
      <Hide ref={hideRef} ok={hideOk} />
      <Terminate ref={terminateRef} ok={terminateOk} />
    </div>
  )
}

export default Datasets
