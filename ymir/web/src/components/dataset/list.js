import React, { useEffect, useRef, useState, version } from "react"
import { connect } from 'dva'
import styles from "./list.less"
import { Link, useHistory, useLocation, useParams } from "umi"
import { Form, Button, Input, Table, Space, Modal, ConfigProvider, Row, Col, Radio, Tooltip, Pagination, } from "antd"

import { format, getUnixTimeStamp } from "@/utils/date"
import t from "@/utils/t"

import { TASKSTATES } from '@/constants/task'
import { states } from '@/constants/dataset'

import StateTag from "@/components/task/stateTag"
import EditBox from "@/components/form/editBox"
import RenderProgress from "@/components/common/progress"
import TypeTag from "@/components/task/typeTag"
import Actions from "@/components/table/actions"

import {
  ImportIcon, ScreenIcon, TaggingIcon, TrainIcon, VectorIcon, SearchIcon,
  TipsIcon, EditIcon, DeleteIcon, TreeIcon
} from "@/components/common/icons"
import { humanize } from "@/utils/number"
import { ArrowDownIcon, ArrowRightIcon } from "../common/icons"
import Del from "./del"
import DelGroup from "./delGroup"

const { confirm } = Modal
const { useForm } = Form

function Datasets({ pid, datasetList, query, versions, getDatasets, delDataset, updateDataset, updateQuery, resetQuery, getVersions, }) {
  const location = useLocation()
  const { name } = location.query
  const history = useHistory()
  const [datasets, setDatasets] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [current, setCurrent] = useState({})
  const delRef = useRef(null)
  const delGroupRef = useRef(null)
  let [lock, setLock] = useState(true)

  /** use effect must put on the top */
  useEffect(() => {
    if (history.action !== 'POP') {
      initState()
    }
    setLock(false)
  }, [history.location])

  useEffect(() => {
    setDatasets(datasetList.items)
    setTotal(datasetList.total)
  }, [datasetList])

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

  useEffect(() => {
    if (location.state?.type) {
      history.replace(location.pathname, {})
    }
  }, [location.state])

  async function initState() {
    await resetQuery()
    form.resetFields()
  }

  const columns = [
    {
      title: showTitle("dataset.column.name"),
      key: "name",
      dataIndex: "versionName",
      className: styles[`column_name`],
      render: (name, { id, state }) => state === states.VALID ? (
        <Link to={`/home/dataset/detail/${id}`}>{name}</Link>
      ) : name,
      ellipsis: true,
    },
    {
      title: showTitle("dataset.column.source"),
      dataIndex: "taskType",
      render: (type) => <TypeTag type={type} />,
      ellipsis: true,
    },
    {
      title: showTitle("dataset.column.asset_count"),
      dataIndex: "assetCount",
      render: (num) => humanize(num),
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
      // sorter: true,
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
  ]

  const actionMenus = (record) => {
    const { id, name, state, versionName } = record
    let actions = []
    const menus = [
      {
        key: "fusion",
        label: t("dataset.action.fusion"),
        onclick: () => history.push(`/home/task/fusion/${id}`),
        icon: <ScreenIcon className={styles.addBtnIcon} />,
      },
      {
        key: "train",
        label: t("dataset.action.train"),
        onclick: () => history.push(`/home/task/train/${id}`),
        icon: <TrainIcon />,
      },
      {
        key: "mining",
        label: t("dataset.action.mining"),
        onclick: () => history.push(`/home/task/mining/${id}`),
        icon: <VectorIcon />,
      },
      {
        key: "label",
        label: t("dataset.action.label"),
        onclick: () => history.push(`/home/task/label/${id}`),
        icon: <TaggingIcon />,
      },
    ]
    const delMenu = {
      key: "del",
      label: t("dataset.action.del"),
      onclick: () => del(id, `${name} ${versionName}`),
      icon: <DeleteIcon />,
    }
    if (isValidDataset(state)) {
      actions = [...menus, delMenu]
    } else {
      actions = [delMenu]
    }
    return actions
  }

  const tableChange = ({ current, pageSize }, filters, sorters = {}) => {
  }

  const listChange = ({ current, pageSize }) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    updateQuery({ ...query, limit, offset })
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  async function getData() {
    getDatasets(pid, query)
  }

  async function showVersions(id) {
    if (!datasets.some(item => item.id === id && item.showVersions)) {
      const result = await getVersions(id)
      if (!result) {
        return
      }
    }
    setDatasets(datasets.map(item => {
      if (item.id === id) {
        item.showVersions = !item.showVersions
      }
      return item
    }))
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

  const edit = (record) => {
    setCurrent({})
    setTimeout(() => setCurrent(record), 0)
  }

  const saveName = async (record, name) => {
    const result = await updateDataset(record.id, name)
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
      updateQuery({ ...query, ...values, })
    } else {
      setTimeout(() => {
        if (name === form.getFieldValue('name')) {
          updateQuery({ ...query, name, })
        }
      }, 1000)
    }
  }


  function isValidDataset(state) {
    return states.VALID === state
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
    getDatasets: (pid, query) => {
      return dispatch({
        type: 'dataset/getDatasetGroups',
        payload: { pid, query },
      })
    },
    getVersions: (gid, force = false) => {
      return dispatch({
        type: 'dataset/getDatasetVersions',
        payload: { gid, force },
      })
    },
    delDataset: (id) => {
      return dispatch({
        type: 'dataset/delDataset',
        payload: id,
      })
    },
    updateDataset: (id, name) => {
      return dispatch({
        type: 'dataset/updateDataset',
        payload: { id, name },
      })
    },
    updateQuery: (query) => {
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
