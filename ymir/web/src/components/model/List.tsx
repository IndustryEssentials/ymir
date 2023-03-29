import { useEffect, useState, useRef } from 'react'
import styles from './list.less'
import { Link, Location, useHistory, useLocation } from 'umi'
import { useSelector } from 'react-redux'
import { Form, Input, Table, Row, Col, Pagination, Space, Empty, Button, message, Popover, TableColumnsType } from 'antd'

import { diffTime } from '@/utils/date'
import { readyState, validState } from '@/constants/common'
import { TASKTYPES, TASKSTATES } from '@/constants/task'
import t from '@/utils/t'
import usePublish from '@/hooks/usePublish'
import { getDeployUrl } from '@/constants/common'
import { getTensorboardLink } from '@/constants/common'

import CheckProjectDirty from '@/components/common/CheckProjectDirty'
import Actions from '@/components/table/Actions'
import TypeTag from '@/components/task/TypeTag'
import RenderProgress from '@/components/common/Progress'
import Terminate, { RefProps as TRefProps } from '@/components/task/terminate'
import Hide, { RefProps } from '../common/hide'
import type { RefProps as ERefProps } from '@/components/form/editBox'
import EditNameBox from '@/components/form/editNameBox'
import EditDescBox from '@/components/form/editDescBox'
import Detail from '@/components/project/Detail'
import EditStageCell from './StageCellEdit'
import { DescPop } from '../common/DescPop'
import useRerunAction from '@/hooks/useRerunAction'

import {
  ShieldIcon,
  VectorIcon,
  EditIcon,
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
import { ModuleType } from '@/pages/project/components/ListHoc'
import useRequest from '@/hooks/useRequest'
import StrongTitle from '../table/columns/StrongTitle'

type IsType = {
  isInitModel?: boolean
}
type ExtraLabel = {
  projectLabel?: string
  iterationLabel?: string
  iterationRound?: number
}
type ModelType = YModels.Model & ExtraLabel & IsType
type ModelGroup = YModels.ModelGroup & ExtraLabel & IsType
type Models = YStates.IdMap<ModelType[]>

const { useForm } = Form

const Model: ModuleType = ({ pid, project, iterations, groups }) => {
  const history = useHistory()
  const location: Location = useLocation()
  const name = location.query?.name
  const [models, setModels] = useState<ModelGroup[]>([])
  const [modelVersions, setModelVersions] = useState<Models>({})
  const [total, setTotal] = useState(1)
  const [selectedVersions, setSelectedVersions] = useState<{ selected: number[]; versions: { [gid: number]: number[] } }>({ selected: [], versions: {} })
  const [form] = useForm()
  const [current, setCurrent] = useState<ModelGroup>()
  const [visibles, setVisibles] = useState<{ [key: number | string]: boolean }>({})
  const [trainingUrl, setTrainingUrl] = useState('')
  let [lock, setLock] = useState(true)
  const editNameBoxRef = useRef<ERefProps>(null)
  const editDescBoxRef = useRef<ERefProps>(null)
  const hideRef = useRef<RefProps>(null)
  const terminateRef = useRef<TRefProps>(null)
  const generateRerun = useRerunAction()
  const [publish, publishResult] = usePublish()
  const [editingModel, setEditingModel] = useState<YModels.Model>()
  const {
    versions,
    query,
    models: { [pid]: modelList },
  } = useSelector<YStates.Root, YStates.ModelState>(({ model }) => model)
  const { run: getModels } = useRequest<YStates.List<YModels.ModelGroup>, [{ pid: number; query: YParams.ModelsQuery }]>('model/getModelGroups')
  const { run: getVersions } = useRequest<YStates.List<YModels.Model>, [{ gid: number; force?: boolean }]>('model/getModelVersions')
  const { run: updateQuery } = useRequest('model/updateQuery')
  const { run: resetQuery } = useRequest('model/resetQuery')

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
    console.log('modelList:', modelList)
    const mds = setGroupLabelsByProject(modelList?.items, project)
    setModels(mds)
    setTotal(modelList?.total || 1)
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
        fetchVersions(Number(gid), true)
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

  useEffect(() => {
    if (name) {
      updateQuery({ ...query, name })
      form.setFieldsValue({ name })
    }
    setLock(false)
  }, [name])

  useEffect(() => {
    console.log('query, lock:', query, lock)
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
    await resetQuery()
    form.resetFields()
  }

  const columns: TableColumnsType<ModelType> = [
    {
      title: <StrongTitle label="model.column.name" />,
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
      title: <StrongTitle label="model.column.source" />,
      dataIndex: 'taskType',
      render: (type) => <TypeTag type={type} />,
    },
    {
      title: <StrongTitle label="model.column.stage" />,
      dataIndex: 'recommendStage',
      render: (_, record) => (validState(record.state) ? <EditStageCell record={record} saveHandle={updateModelVersion} /> : null),
      // align: 'center',
      width: 300,
    },
    {
      title: <StrongTitle label="dataset.column.state" />,
      dataIndex: 'state',
      render: (state, record) => RenderProgress(state, record),
      // width: 60,
    },
    {
      title: <StrongTitle label="model.column.create_time" />,
      dataIndex: 'createTime',
      sorter: (a, b) => diffTime(a.createTime, b.createTime),
      width: 200,
      align: 'center',
    },
    {
      title: <StrongTitle label="model.column.action" />,
      key: 'action',
      dataIndex: 'action',
      render: (text, record) => <Actions actions={actionMenus(record)} showCount={3} />,
      className: styles.tab_actions,
      align: 'center',
      width: '280px',
    },
  ]

  const hideHidden = ({ state, id }: YModels.Model) => readyState(state) || project?.hiddenModels?.includes(id)

  const listChange = (current: number, pageSize: number) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    updateQuery({ ...query, current, limit, offset })
  }

  function updateModelVersion(result: YModels.Model) {
    setModelVersions((mvs) => {
      return {
        ...mvs,
        [result.groupId]: mvs[result.groupId].map((version) => {
          return version.id === result.id ? result : version
        }),
      }
    })
  }

  async function showVersions(id: number) {
    setVisibles((old) => ({ ...old, [id]: !old[id] }))
  }

  function setVersionLabelsByIterations(versions: Models, iterations: YModels.Iteration[]) {
    Object.keys(versions).forEach((gid) => {
      const list = versions[gid]
      const updatedList = list.map((item) => {
        delete item.iterationLabel
        return setLabelByIterations(item, iterations)
      })
      versions[gid] = updatedList
    })
    return { ...versions }
  }

  function setVersionLabelsByProject(versions: Models, project?: YModels.Project) {
    Object.keys(versions).forEach((gid) => {
      const list = versions[gid]
      const updatedList = list.map((item) => {
        delete item.projectLabel
        return project?.model ? setLabelByProject(project?.model, 'isInitModel', item) : item
      })
      versions[gid] = updatedList
    })
    return { ...versions }
  }

  function setGroupLabelsByProject(items: ModelGroup[] = [], project?: YModels.Project) {
    return items.map((item) => {
      delete item.projectLabel
      return project?.model ? setLabelByProject(project?.model, 'isInitModel', item) : item
    })
  }

  function setLabelByProject<T extends ModelType | ModelGroup = ModelType>(id: number, label: keyof IsType, item: T, version = ''): T {
    const maps = {
      isInitModel: 'project.tag.model',
    }
    item[label] = !!id && item.id === id
    item.projectLabel = item.projectLabel || (item[label] ? t(maps[label], { version }) : '')
    return item
  }

  function setLabelByIterations(item: ModelType, iterations?: YModels.Iteration[]) {
    const iteration = iterations?.find((iter) =>
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

  function fetchVersions(id: number | string, force?: boolean) {
    getVersions({ gid: Number(id), force })
  }

  function getData() {
    console.log('pid, query:', pid, query)
    getModels({ pid, query })
  }

  const actionMenus = (record: ModelType): YComponents.Action[] => {
    const { id, name, url, state, taskState, taskType, task, isProtected, stages, recommendStage } = record

    const actions = [
      {
        key: 'publish',
        label: t('model.action.publish'),
        hidden: () => !validState(state) || !getDeployUrl(),
        onclick: () => publish(record),
        icon: <ShieldIcon />,
      },
      {
        key: 'verify',
        label: t('model.action.verify'),
        hidden: () => !validState(state),
        onclick: () => history.push(`/home/project/${pid}/model/${id}/verify`),
        icon: <ShieldIcon />,
      },
      {
        key: 'download',
        label: t('model.action.download'),
        link: url,
        target: '_blank',
        hidden: () => !validState(state),
        icon: <FileDownloadIcon />,
      },
      {
        key: 'mining',
        label: t('dataset.action.mining'),
        hidden: () => !validState(state),
        onclick: () => history.push(`/home/project/${pid}/mining?mid=${id},${recommendStage}`),
        icon: <VectorIcon />,
      },
      {
        key: 'train',
        label: t('dataset.action.train'),
        hidden: () => !validState(state),
        onclick: () => history.push(`/home/project/${pid}/train?mid=${id},${recommendStage}`),
        icon: <TrainIcon />,
      },
      {
        key: 'inference',
        label: t('dataset.action.inference'),
        hidden: () => !validState(state),
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
        hidden: () => taskState === TASKSTATES.PENDING || !readyState(state) || task.is_terminated,
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
        label: t('common.action.del'),
        onclick: () => hide(record),
        hidden: () => hideHidden(record),
        icon: <DeleteIcon />,
      },
    ]
    return actions
  }

  const edit = (record: ModelGroup) => {
    editNameBoxRef.current?.show()
    setCurrent(record)
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
      hideRef.current?.hide(vss, project?.hiddenModels)
    } else {
      message.warning(t('model.list.batch.invalid'))
    }
  }

  const getDisabledStatus = (filter?: (v: ModelType) => boolean) => {
    const allVss = Object.values(versions).flat()
    const { selected } = selectedVersions
    return !selected.length || (filter && allVss.filter(({ id }) => selected.includes(id)).some(filter))
  }

  const hide = (version: ModelType) => {
    if (project?.hiddenModels.includes(version.id)) {
      return message.warn(t('dataset.del.single.invalid'))
    }
    hideRef.current?.hide([version])
  }

  const hideOk = (result: YModels.Result[]) => {
    result.forEach((item) => fetchVersions(item.groupId, true))
    getData()
    setSelectedVersions({ selected: [], versions: {} })
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

  const stop = (model: ModelType) => {
    terminateRef.current?.confirm(model)
  }

  function terminateOk({}, { groupId }: YModels.Result) {
    groupId && fetchVersions(groupId, true)
  }

  const saveNameHandle = (result: ModelGroup) => {
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
  const saveDescHandle = (result: ModelType) => {
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

  const editDesc = (model: ModelType) => {
    editDescBoxRef.current?.show()
    setEditingModel(model)
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
      <Button type="primary" disabled={getDisabledStatus(({ state }) => readyState(state))} onClick={multipleHide}>
        <DeleteIcon /> {t('common.action.multiple.del')}
      </Button>
      <Button type="primary" disabled={getDisabledStatus(({ state }) => !validState(state))} onClick={multipleInfer}>
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
                  rowKey={(record) => record.id}
                  rowSelection={{
                    selectedRowKeys: selectedVersions.versions[group.id],
                    onChange: (keys) => rowSelectChange(group.id, keys as number[]),
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
      <Detail type='model' project={project} />
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
          <Form name="queryForm" form={form} labelCol={{ flex: '120px' }} initialValues={{ name: name || query.name }} onValuesChange={search} colon={false}>
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
      <EditNameBox ref={editNameBoxRef} type="model" record={current} max={80} handle={saveNameHandle} />
      <EditDescBox ref={editDescBoxRef} type="model" record={editingModel} handle={saveDescHandle} />
      <Hide ref={hideRef} type={'model'} msg="model.action.del.confirm.content" ok={hideOk} />
      <Terminate ref={terminateRef} ok={terminateOk} />
    </div>
  )
}

// const props = (state) => {
//   return {
//     logined: state.user.logined,
//     query: state.model.query,
//     versions: state.model.versions,
//   }
// }

// const actions = (dispatch) => {
//   return {
//     getModels: (pid, query) => {
//       return dispatch({
//         type: 'model/getModelGroups',
//         payload: { pid, query },
//       })
//     },
//     getVersions: (gid, force) => {
//       return dispatch({
//         type: 'model/getModelVersions',
//         payload: { gid, force },
//       })
//     },
//     updateQuery: (query) => {
//       return dispatch({
//         type: 'model/updateQuery',
//         payload: query,
//       })
//     },
//     resetQuery: () => {
//       return dispatch({
//         type: 'model/resetQuery',
//       })
//     },
//   }
// }

export default Model
