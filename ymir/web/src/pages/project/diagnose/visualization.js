import React, { useEffect, useRef, useState } from "react"
import useFetch from '@/hooks/useFetch'
import ReactJson from 'react-json-view'
import { Button, Form, Input, Row, Col, Space, Table, Popover, InputNumber, Slider, message } from 'antd'
import { SyncOutlined } from "@ant-design/icons"
import { SearchIcon, EyeOnIcon, DeleteIcon } from "@/components/common/icons"

import t from "@/utils/t"
import s from './visualization.less'
import Panel from "@/components/form/panel"
import Actions from "@/components/table/actions"
import InferResultSelect from "@/components/form/inferResultSelect"
import Del from './components/del'

const initQuery = {
  name: "",
  current: 1,
  offset: 0,
  limit: 10,
}

const sameConfig = (config, config2) => {
  return JSON.stringify(config2) === JSON.stringify(config)
}
const sameConfigs = (config, configs) => {
  return configs.some(item => sameConfig(item, config))
}

function Visualization({ pid, project }) {
  const [createForm] = Form.useForm()
  const [queryForm] = Form.useForm()
  const [settingsVisible, setSettingsVisible] = useState(true)
  const [createResult, createVisualization] = useFetch('visualization/createVisualization')
  const [{ items, total }, fetchSource] = useFetch('visualization/getVisualizations', { items: [], total: 0 })
  const [modelStages, fetchModelStages] = useFetch('model/batchModelStages', [])
  const [datasets, fetchDatasets] = useFetch('dataset/batchDatasets', [])
  const [tableSource, setTableSource] = useState([])
  const [query, setQuery] = useState(initQuery)
  const delRef = useRef(null)
  const [taskIds, setTaskIds] = useState([])
  const inferRef = useRef(null)

  useEffect(() => {
    getData()
  }, [query, createResult])

  useEffect(() => {
    setTableData(items)
    fetchBatchData(items)
  }, [items])


  useEffect(() => {
    const source = tableSource?.map(item => {
      return {
        ...item,
        modelStages: modelStages?.length && modelStages?.filter(stage => item.modelStageIds.includes(stage.id)) || [],
        datasets: datasets?.length && datasets?.filter(dataset => item.datasetIds.includes(dataset.id)) || []
      }
    })
    setTableSource(source)
  }, [modelStages, datasets])

  async function getData() {
    let params = {
      ...query,
      projectId: pid,
    }
    if (query.name) {
      params.name = query.name.toLowerCase()
    }
    fetchSource(params)
  }

  function setTableData(items) {
    const source = items.map(item => {
      const itemSatgeIds = item.tasks.map(task => task?.parameters?.model_stage_id)
      const itemDatasetIds = item.tasks.map(task => task?.parameters?.dataset_id)
      return {
        ...item,
        modelStageIds: itemSatgeIds,
        datasetIds: itemDatasetIds,
      }
    })
    setTableSource(source)
  }

  function fetchBatchData(items) {
    const stageIds = [...new Set(items.map(item => item.tasks.map(task => task?.parameters?.model_stage_id)).flat())].filter(id => id)
    const datasetIds = [...new Set(items.map(item => item.tasks.map(task => task?.parameters?.dataset_id)).flat())].filter(id => id)
    stageIds?.length && fetchModelStages(stageIds)
    datasetIds?.length && fetchDatasets({ pid, ids: datasetIds })
  }

  function InferResultChange(tasks) {
    setTaskIds(tasks.map(task => task.id))
  }

  const onFinish = async (values) => {
    if (!taskIds.length) {
      return message.error('model.diagnose.v.tasks.require')
    }
    const params = {
      ...values,
      projectId: pid,
      taskIds,
    }
    createVisualization(params)
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  function getModelNames(stages = []) {
    return stages.map(stage => `${stage.modelName} ${stage.name}`)
  }

  function getDatasetNames(datasets = []) {
    return datasets.map(dataset => `${dataset.name} ${dataset.versionName}`)
  }

  function renderName(names) {
    return renderPop(names.toString(), (<div>{names.map(name => <div key={name}>{name}<br /></div>)}</div>), 300)
  }

  const columns = [
    {
      title: showTitle('visualization.column.model'),
      dataIndex: "modelStageIds",
      ellipsis: true,
      render: (ids, { modelStages }) => {
        return modelStages ? renderName(getModelNames(modelStages)) : ids.join(',')
      },
    },
    {
      title: showTitle('visualization.column.dataset'),
      dataIndex: "datasetIds",
      ellipsis: true,
      render: (ids, { datasets }) => {
        return datasets ? renderName(getDatasetNames(datasets)) : ids.join(',')
      },
    },
    {
      title: showTitle('model.diagnose.label.config'),
      dataIndex: "tasks",
      render: (tasks) => {
        const configs = tasks.map(({ config }) => config).reduce((prev, curr) => sameConfigs(curr, prev) ? prev : [...prev, curr], [])
        return configs.map((config, index) => {
          const rlabel = `config${index + 1} `
          return <span key={rlabel}>{config ? renderPop(rlabel, (<ReactJson src={config} name={false} />)) : rlabel}</span>
        })
      },
    },
    {
      title: showTitle('model.diagnose.form.iou'),
      dataIndex: 'iou',
      width: 100,
    },
    {
      title: showTitle('model.diagnose.form.confidence'),
      dataIndex: 'confidence',
      width: 80,
    },
    {
      title: showTitle("visualization.column.create_time"),
      dataIndex: "createTime",
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: 'descend',
      width: 180,
    },
    {
      title: showTitle("visualization.column.action"),
      dataIndex: "id",
      render: (text, record) => <Actions menus={actionMenus(record)} />,
      align: "center",
      width: 150,
    },
  ]

  function renderPop(label, content = {}) {
    return <Popover content={content} >
      <span>{label}</span>
    </Popover>
  }

  const actionMenus = (record) => {
    const { id, tid } = record
    const menus = [
      {
        key: "view",
        label: t("common.view"),
        onclick: () => window.open(`/fiftyone/app/?tid=${tid}`, '_blank'),
        icon: <EyeOnIcon />,
      },
      {
        key: "del",
        label: t("common.del"),
        onclick: () => del(id),
        icon: <DeleteIcon />,
      },
    ]
    return menus
  }

  const del = (id, name) => {
    delRef.current.del(id, name)
  }

  const delOk = (id) => {
    getData()
  }

  const pageChange = ({ current, pageSize }, filters, sorters) => {
    const is_desc = sorters.order !== 'ascend'
    const sortColumn = sorters.field === 'createTime' ? 'create_datetime' : undefined
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery(old => ({
      ...old,
      current,
      limit,
      offset,
      order_by: sorters.column ? sortColumn : 'id',
      is_desc
    }))
  }

  const search = (values) => {
    const name = values.name
    if (typeof name === 'undefined') {
      setQuery((old) => ({
        ...old,
        ...values,
        offset: initQuery.offset,
      }))
    } else {
      setTimeout(() => {
        if (name === queryForm.getFieldValue('name')) {
          setQuery((old) => ({
            ...old,
            name,
            offset: initQuery.offset,
          }))
        }
      }, 1000)
    }
  }

  const reset = () => {
    createForm.resetFields();
  }

  return (
    <div className={s.wrapper}>
      <div className={s.container}>
        <Form
          name='createForm'
          className={s.form}
          form={createForm}
          labelCol={{ span: 4, offset: 2 }}
          wrapperCol={{ span: 10 }}
          layout='horizontal'
          labelAlign={'left'}
          colon={false}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
        >
          <InferResultSelect pid={pid} form={createForm} onChange={({ tasks }) => InferResultChange(tasks)} />

          <Form.Item label={t('model.diagnose.form.confidence')} name='confidence' initialValue={0.5}>
            <InputNumber step={0.0005} min={0.0005} max={0.9995} />
          </Form.Item>
          <Form.Item label={'IOU'} name='iou' initialValue={0.5}>
            <Slider min={0.25} max={0.95} step={0.05} marks={{ 0.25: '0.25', 0.5: '0.5', 0.95: '0.95' }} />
          </Form.Item>
          <Form.Item wrapperCol={{ offset: 6 }}>
            <Space size={20} style={{ display: 'flex' }}>
              <Form.Item name='submitBtn'>
                <Button type="primary" size="large" htmlType="submit">
                  {t('common.confirm')}
                </Button>
              </Form.Item>
              <Form.Item name='backBtn'>
                <Button size="large" onClick={() => reset()}>
                  {t('common.cancel')}
                </Button>
              </Form.Item>
            </Space>
          </Form.Item>
        </Form>
        <Panel label={t('visualization.records.title')} visible={settingsVisible} setVisible={() => setSettingsVisible(!settingsVisible)}>
          <div className={s.tableContainer}>
            <div className={`search ${s.search}`}>
              <Form
                name='queryForm'
                form={queryForm}
                labelCol={{ flex: '120px' }}
                onValuesChange={search}
                colon={false}
              >
                <Row>
                  <Col className={s.queryColumn} span={12}>
                    <Form.Item name="name" label={t("visualization.query.name")}>
                      <Input placeholder={t("visualization.form.name.placeholder")} style={{ width: '80%' }} allowClear suffix={<SearchIcon />} />
                    </Form.Item>
                  </Col>
                </Row>
              </Form>
            </div>
            <Row>
              <Col flex={1}>
              </Col>
              <Col>
                <Button
                  type='text'
                  icon={<SyncOutlined style={{ color: 'rgba(0, 0, 0, 0.45)' }} />}
                  title={'Refresh'}
                  onClick={() => getData()}
                ></Button>
              </Col>
            </Row>
            <Table
              align='center'
              dataSource={tableSource}
              onChange={pageChange}
              rowKey={(record) => record.id}
              rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
              pagination={{
                showQuickJumper: true,
                showSizeChanger: true,
                total: total,
                defaultPageSize: query.limit,
                showTotal: (total) => t("keyword.pager.total.label", { total }),
                defaultCurrent: query.current,
                current: query.current,
              }}
              columns={columns}
            />
          </div>
        </Panel>
        <Del ref={delRef} ok={delOk} />
      </div>
    </div >
  )
}

export default Visualization
