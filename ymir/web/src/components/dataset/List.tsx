import { ComponentProps, useCallback, useEffect, useRef, useState } from 'react'
import { Link, Location, useHistory, useLocation, useSelector } from 'umi'
import { Form, Button, Input, Table, Space, Row, Col, Tooltip, Pagination, message, Popover, TableColumnsType } from 'antd'

import t from '@/utils/t'
import { diffTime } from '@/utils/date'
import { getTaskTypeLabel, TASKSTATES, TASKTYPES } from '@/constants/task'
import { DefaultShowVersionCount, getLabelToolUrl, readyState, validState } from '@/constants/common'
import { canHide, validDataset } from '@/constants/dataset'
import useRequest from '@/hooks/useRequest'

import CheckProjectDirty from '@/components/common/CheckProjectDirty'
import type { RefProps as ERefProps } from '@/components/form/editBox'
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
import { DescPop } from '../common/DescPop'
import useRerunAction from '@/hooks/useRerunAction'
import StrongTitle from '../table/columns/StrongTitle'
import { ModuleType } from '@/pages/project/components/ListHoc'
import useModal from '@/hooks/useModal'
import Analysis from './Analysis'
import { getActions } from './list/Actions'

import styles from './list.less'
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
  BarChart2LineIcon,
  ArrowUpIcon,
} from '@/components/common/Icons'
import { ObjectType } from '@/constants/objectType'
import SimpleSuggestion from './list/SimpleSuggestion'
import { IdMap, List } from '@/models/typings/common.d'
import Empty from '../empty/Dataset'
import { Dataset as DatasetType, DatasetGroup as DatasetGroupType, Iteration, Project, Result, Task } from '@/constants'
import IterationRoundTag from '../table/IterationRoundTag'
import IterationTypeTag from '../table/IterationTypeTag'

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
type Dataset = DatasetType & ExtraLabel & IsType
type DatasetGroup = DatasetGroupType & ExtraLabel & IsType
type VersionsType = IdMap<Dataset[]>

const { useForm } = Form

const Datasets: ModuleType = ({ pid, project, iterations, groups }) => {
  const location: Location<{ type: string }> = useLocation()
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
  const editNameBoxRef = useRef<ERefProps>(null)
  const editDescBoxRef = useRef<ERefProps>(null)
  let [lock, setLock] = useState(true)
  const terminateRef = useRef<TRefProps>(null)
  const [testingSetIds, setTestingSetIds] = useState<number[]>([])
  const generateRerun = useRerunAction()
  const [editingDataset, setEditingDataset] = useState<Dataset>()
  const {
    datasets: { [pid]: datasetList },
    versions,
    query,
  } = useSelector(({ dataset }) => dataset)

  const { run: getDatasets } = useRequest<List<DatasetGroup>>('dataset/getDatasetGroups')
  const { run: getVersions } = useRequest<List<Dataset>, [{ gid: number; force?: boolean }]>('dataset/getDatasetVersions')
  const { run: updateQuery } = useRequest('dataset/updateQuery')
  const { run: resetQuery } = useRequest('dataset/resetQuery')
  const [datasetAdded, setDatasetAdded] = useState(false)
  const [AnalysisModal, showAnalysisModal] = useModal<ComponentProps<typeof Analysis>>(Analysis, {
    width: '90%',
    style: { paddingTop: 20 },
  })
  const [analysisDatasets, setADatasets] = useState<number[]>([])
  const { data: modelsCount = 0, run: getModelsCount } = useRequest<number, [number]>('model/getValidModelsCount', { loading: false })
  const { data: imagesCount = 0, run: getImagesCount } = useRequest<number, [{ type?: ObjectType; example?: boolean }]>('image/getValidImagesCount', {
    loading: false,
  })

  useEffect(() => {
    getModelsCount(pid)
  }, [pid])
  useEffect(() => {
    project && getImagesCount({ type: project.type, example: true })
  }, [project])

  useEffect(() => {
    const datasets = Object.values(versions)
      .flat()
      .filter((ds) => ds.projectId === pid)
    const added = datasets.filter((dataset) => validState(dataset.state) || readyState(dataset.state))
    setDatasetAdded(!!added.length)
  }, [versions])

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
    setDatasets(datasetList?.items || [])
    setTotal(datasetList?.total || 1)
  }, [datasetList])

  useEffect(() => {
    setTestingSetIds(project?.testingSets || [])
  }, [project])

  useEffect(() => {
    Object.keys(visibles).map((key) => {
      const k = Number(key)
      if (visibles[k]) {
        fetchVersions(k)
      }
    })
  }, [visibles])

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
        render: (name, record) => {
          const { id, description, projectLabel, state, assetCount } = record
          const popContent = <DescPop description={description} style={{ maxWidth: '30vw' }} />
          const content = (
            <Row key={id}>
              <Col flex={1}>{readyState(state) ? name : <Link to={`/home/project/${pid}/dataset/${id}`}>{name}</Link>}</Col>
              <Col flex={'50px'} style={{ textAlign: 'right' }}>
                <IterationTypeTag project={project} id={id} />
                <IterationRoundTag iterations={iterations} id={id} />
                {validState(state) && assetCount ? (
                  <span
                    onClick={(e) => {
                      e.stopPropagation()
                      showAnalysisModal()
                      setADatasets([id])
                    }}
                  >
                    <BarChart2LineIcon />
                  </span>
                ) : null}
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
        title: <StrongTitle label="dataset.column.suggestion" />,
        dataIndex: 'suggestions',
        render: (suggestions) => <SimpleSuggestion suggestions={suggestions} />,
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

  const actionMenus = useCallback(
    (record: Dataset): YComponents.Action[] => {
      const { id, groupId, state, taskState, task, assetCount } = record
      const invalidDataset = ({ state, assetCount }: Dataset) => !validState(state) || assetCount === 0
      const acts = {
        label: {
          key: 'label',
          label: t('dataset.action.label'),
          hidden: () => invalidDataset(record),
          onclick: () => history.push(`/home/project/${pid}/label?did=${id}`),
          icon: <TaggingIcon />,
        },
        train: {
          key: 'train',
          label: t('dataset.action.train'),
          hidden: () => invalidDataset(record) || isTestingDataset(id),
          onclick: () => history.push(`/home/project/${pid}/train?did=${id}`),
          icon: <TrainIcon />,
        },
        mining: {
          key: 'mining',
          label: t('dataset.action.mining'),
          hidden: () => invalidDataset(record),
          onclick: () => history.push(`/home/project/${pid}/mining?did=${id}`),
          icon: <VectorIcon />,
        },
        merge: {
          key: 'merge',
          label: t('common.action.merge'),
          hidden: () => !validState(state),
          onclick: () => history.push(`/home/project/${pid}/merge?did=${id}`),
          icon: <CompareListIcon className={styles.addBtnIcon} />,
        },
        filter: {
          key: 'filter',
          label: t('common.action.filter'),
          hidden: () => invalidDataset(record),
          onclick: () => history.push(`/home/project/${pid}/filter?did=${id}`),
          icon: <ScreenIcon className={styles.addBtnIcon} />,
        },
        inference: {
          key: 'inference',
          label: t('dataset.action.inference'),
          hidden: () => invalidDataset(record),
          onclick: () => history.push(`/home/project/${pid}/inference?did=${id}`),
          icon: <WajueIcon />,
        },
        copy: {
          key: 'copy',
          label: t('task.action.copy'),
          hidden: () => invalidDataset(record),
          onclick: () => history.push(`/home/project/${pid}/copy?did=${id}`),
          icon: <CopyIcon />,
        },
        edit: {
          key: 'edit',
          label: t('common.action.edit.desc'),
          onclick: () => editDesc(record),
          icon: <EditIcon />,
        },
        stop: {
          key: 'stop',
          label: t('task.action.terminate'),
          onclick: () => stop(record),
          hidden: () => taskState === TASKSTATES.PENDING || !readyState(state) || task.is_terminated,
          icon: <StopIcon />,
        },
        rerun: generateRerun(record),
        del: {
          key: 'del',
          label: t('common.action.del'),
          onclick: () => hide(record),
          hidden: () => !canHide(record, project),
          icon: <DeleteIcon />,
        },
        labeltool: {
          key: 'labeltool',
          label: t('dataset.action.labeltool'),
          link: getLabelToolUrl(),
          target: '_blank',
        },
      }
      const normalActions = getActions(acts, {
        hasImages: !!imagesCount,
        haveAnnotations: !!record.keywords.length,
        haveModels: !!modelsCount,
      })
      if (record.taskType === TASKTYPES.LABEL) {
        return [acts.labeltool, ...normalActions]
      }
      return normalActions
    },
    [modelsCount, imagesCount, versions],
  )

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

  function toggleVersions(id: number, force?: boolean) {
    setVisibles((old) => ({ ...old, [id]: force || (typeof old[id] !== 'undefined' && !old[id]) }))
  }

  function fetchVersions(gid: number, force?: boolean) {
    getVersions({ gid, force })
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

  function terminateOk(t: Task, ds: Result) {
    ds?.groupId && fetchVersions(ds.groupId, true)
  }

  const edit = (record: DatasetGroup) => {
    editNameBoxRef.current?.show()
    setCurrent(record)
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

  const editDesc = (dataset: Dataset) => {
    editDescBoxRef.current?.show()
    setEditingDataset(dataset)
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

  const hideOk = (result: { groupId: number }[]) => {
    result.forEach((item) => item?.groupId && fetchVersions(item?.groupId, true))
    fetchDatasets()
    setSelectedVersions({ selected: [], versions: {} })
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
      <Button type="primary" disabled={getDisabledStatus(({ state }) => !validState(state))} onClick={batchMerge}>
        <WajueIcon /> {t('common.action.multiple.merge')}
      </Button>
    </>
  )

  const renderGroups = datasets.length ? (
    <>
      <div className="groupList">
        {datasets.map((group) => (
          <div className={styles.groupItem} key={group.id}>
            <Row className="groupTitle">
              <Col flex={1} onClick={() => toggleVersions(group.id)}>
                <span className="foldBtn">{visibles[group.id] !== false ? <ArrowDownIcon /> : <ArrowRightIcon />} </span>
                <span className="groupName">{group.name}</span>
                <IterationTypeTag project={project} gid={group.id} />
              </Col>
              <Col>
                <Space>
                  <a onClick={() => edit(group)} title={t('common.modify')}>
                    <EditIcon />
                  </a>
                </Space>
              </Col>
            </Row>
            <div className="groupTable" hidden={visibles[group.id] === false}>
              <Table
                dataSource={typeof visibles[group.id] === 'undefined' ? (versions[group.id] || []).slice(0, DefaultShowVersionCount) : versions[group.id]}
                rowKey={(record) => record.id}
                rowSelection={{
                  selectedRowKeys: selectedVersions.versions[group.id],
                  onChange: (keys) => rowSelectChange(group.id, keys as number[]),
                }}
                rowClassName={(record, index) => (index % 2 === 0 ? '' : 'oddRow')}
                columns={columns(group.id)}
                pagination={false}
              />
              {!visibles[group.id] && (group.versions?.length || 0) > DefaultShowVersionCount ? (
                <div style={{ textAlign: 'center' }}>
                  <Button type="link" className="moreVersion" onClick={() => toggleVersions(group.id, true)}>
                    <ArrowDownIcon /> {t('dataset.unfold.all')}
                  </Button>
                </div>
              ) : null}
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
  ) : (
    <Empty />
  )

  return (
    <div className={styles.dataset}>
      <Detail pid={pid} type="dataset" />
      <Row className="actions">
        <Col flex={1}>
          <Space>
            <AddButton className={!datasetAdded ? 'scale' : ''} />
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
            initialValues={{ type: query.type, name: name || query.name }}
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
      <EditDescBox ref={editDescBoxRef} record={editingDataset} />
      <EditNameBox ref={editNameBoxRef} record={current} max={80} handle={saveNameHandle} />
      <Hide ref={hideRef} ok={hideOk} />
      <Terminate ref={terminateRef} ok={terminateOk} />
      <AnalysisModal ids={analysisDatasets} />
    </div>
  )
}

export default Datasets
