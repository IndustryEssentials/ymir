import Graphin, { Utils, Behaviors, GraphinContext, registerFontFamily } from '@antv/graphin'
import { useContext, useEffect, useRef, useState } from 'react'
import { Link, useParams, useHistory } from 'umi'
import { connect } from 'dva'
import { Button, Card, Col, Descriptions, Row, Space, Tag } from 'antd'

import { TASKTYPES } from '@/constants/task'
import { HISTORYNODETYPES } from '@/constants/history'
import { format } from '@/utils/date'
import t from '@/utils/t'

import styles from './index.less'
import '@antv/graphin/dist/index.css'
import '@antv/graphin-components/dist/index.css'
import '@antv/graphin-icons/dist/index.css'
import Breadcrumbs from '@/components/common/breadcrumb'
import { Legend } from '@antv/graphin-components'
import { JiedianIcon } from '@/components/common/icons'

import fonts from '@/assets/icons/iconfont.json'



const { FitView, ZoomCanvas, ClickSelect, } = Behaviors
const { Item } = Descriptions

const iconLoader = () => {
  return {
    fontFamily: 'iconfont',
    glyphs: fonts.glyphs,
  }
}
const { fontFamily } = iconLoader()
const icons = registerFontFamily(iconLoader)

// const data = transferData(Utils.mock(15).tree().graphin())
const layout = {
  type: 'dagre',
  // rankdir: 'BT',
  // align: 'UL',
  ranksep: 30,
  nodesep: 50,
}

const nodeStateStyles = {
  status: {
    selected: {
      halo: {
        fill: "#fff",
        strokeWidth: 1,
      },
    },
  },
}

// behaviors
// click node
const ClickNode = ({ handle }) => {
  const { graph } = useContext(GraphinContext)
  useEffect(() => {
    const handler = (ev) => {
      handle(ev)
    }
    graph.on('node:click', handler)
    return () => {
      graph.off('node:click', handler)
    }
  }, [])

  return null
}

// click edge
const ClickEdge = ({ handle }) => {
  const { graph } = useContext(GraphinContext)
  useEffect(() => {
    const handler = (ev) => {
      handle(ev)
    }
    graph.on('edge:click', handler)
    return () => {
      graph.off('edge:click', handler)
    }
  }, [])
  return null
}

function transferData(data, type, id) {
  const result = {}
  const nodeStyle = {
    model: {
      color: '#F2637B',
      icon: icons['nav-modelmanage'],
    },
    dataset: {
      color: '#67D7D8',
      icon: icons['nav-dataset'],
    }
  }
  const edgeStyle = {
    [TASKTYPES.MINING]: {
      color: 'rgba(250, 211, 55, 0.75)',
      label: 'M',
    },
    [TASKTYPES.TRAINING]: {
      color: 'rgba(44, 189, 233, 0.75)',
      label: 'T',
    },
    [TASKTYPES.FILTER]: {
      color: 'rgba(242, 99, 123, 0.75)',
      label: 'F',
    },
    [TASKTYPES.LABEL]: {
      color: 'rgba(53, 202, 203, 0.75)',
      label: 'L',
    },
  }
  result.nodes = data.nodes.map(node => {
    const key = node.type === HISTORYNODETYPES.DATASET ? 'dataset' : 'model'
    const { color, icon } = nodeStyle[key]

    const isOrigin = type === key && node.id == id
    const config = {
      id: node.hash,
      data: { type: node.type, id: node.id, key, origin: isOrigin },
      style: {
        keyshape: {
          fill: color,
          fillOpacity: 0.2,
          stroke: color,
          size: 50,
        },
        label: {
          value: node.name,
          fontSize: 14,
          offset: [0, 5],
        },
        icon: {
          type: 'font',
          fontFamily,
          value: icon,
          fill: color,
          size: 20,
        }
      },
    }

    if (isOrigin) {
      config.style.icon.fill = '#fff'
      config.style.keyshape.fillOpacity = 1
      config.style.label.fill = color
      // config.style.halo = {
      //   visible: true,
      //   stroke: 'red',
      //   lineWidth: 3,
      //   fill: 'red'
      // }
    }

    return config
  })
  result.edges = data.edges.map(({ target, source, task = {} }) => {
    const type = edgeStyle[task.type] ? task.type : 1
    const { color, label } = edgeStyle[type]
    return {
      target,
      source,
      style: {
        keyshape: {
          stroke: color,
          lineWidth: 3,
        },
        label: {
          value: label,
          fontSize: 20,
          fill: color,
          offset: [0, 20]
        },
      },
    }
  })
  return result
}

function History({ getHistory, getDataset, getModel }) {
  const history = useHistory()
  const { type, id } = useParams()
  const [netData, setNetData] = useState({ edges: [], nodes: [] })
  const [cavasHeight, setCavasHeight] = useState(0)
  const [selectedNode, setSelectedNode] = useState({})

  useEffect(() => {
    setCavasHeight(document.documentElement.clientHeight - 295)
  }, [])

  useEffect(async () => {
    const result = await getHistory(type, id)
    if (result) {
      setNetData(transferData(result, type, id))
    }
  }, [type, id])

  useEffect(() => {
    id && type && getNodeData(id, HISTORYNODETYPES[type.toUpperCase()])
  }, [type, id])


  function clickNode({ item, target }) {
    const nodeModel = item.getModel()
    const { id, type } = nodeModel.data
    getNodeData(id, type)
  }

  async function getNodeData(id, type) {
    // get dataset or model
    if (type === HISTORYNODETYPES.DATASET) {
      const result = await getDataset(id)
      if (result) {
        setSelectedNode({ data: result, type })
      }
    } else {
      const result = await getModel(id)
      if (result) {
        setSelectedNode({ data: result, type })
      }
    }
  }

  function clickEdge(ev) {
    // do nothing now
  }

  function renderDatasetLink (sets) {
    return sets.map(set => <Link className={styles.link} key={set.id} to={`/home/dataset/detail/${set.id}`}>{set.name}</Link>)
  }

  const renderTitle = (
    <Row>
      <Col flex={1}>{t('breadcrumbs.history')}</Col>
      <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
    </Row>
  )

  function renderGraph() {
    return (
      <Graphin data={netData} layout={layout} fitCenter={true} height={cavasHeight} nodeStateStyles={nodeStateStyles}>
        {/* <FitView /> */}
        <ClickSelect />
        <ClickNode handle={clickNode} />
        <ClickEdge handle={clickEdge} />
        <ZoomCanvas />
        <Legend bindType="node" sortKey="data.key" colorKey="style.keyshape.stroke">
          <Legend.Node />
        </Legend>
      </Graphin>
    )
  }

  function renderDataset() {
    const dataset = selectedNode.data
    return dataset.id ? (
      <Descriptions column={1} bordered contentStyle={{ padding: '20px 0 20px 10px', flexWrap: 'wrap' }} labelStyle={{ padding: '20px 0 20px 10px', width: '80px', justifyContent: 'flex-end' }}>
        <Item label={t('dataset.column.name')}>{dataset.name}</Item>
        <Item label={t('dataset.column.asset_count')}>{dataset.asset_count}</Item>
        <Item label={t('dataset.column.keyword')}>{dataset.keywords.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}</Item>
        <Item label={t('dataset.column.create_time')}>{format(dataset.create_datetime)}</Item>
        <Item>
          <Space>
            <Link to={`/home/dataset/detail/${dataset.id}`}>{t('dataset.action.detail')}</Link>
          </Space>
        </Item>
      </Descriptions>
    ) : null
  }

  function renderModel() {
    const model = selectedNode.data
    return model ? (
      <Descriptions column={1} bordered contentStyle={{ padding: '20px 0 20px 10px', flexWrap: 'wrap' }} labelStyle={{ padding: '20px 0 20px 10px', width: '80px', justifyContent: 'flex-end' }}>
        <Item label={t('model.column.name')}>{model.name}</Item>
        <Item label={t('model.detail.label.source')}><Link to={`/home/task/detail/${model.task_id}`}>{model.task_name}</Link></Item>
        <Item label={t('model.detail.label.training_dataset')}>{renderDatasetLink(model.trainSets)}</Item>
        <Item label={t('model.detail.label.test_dataset')}>{renderDatasetLink(model.testSets)}</Item>
        {/* <Item label={t('model.detail.label.train_type')}>{model.parameters?.train_type}</Item> */}
        <Item label={t('model.detail.label.train_goal')}>{model.keywords?.map(keyword => (<Tag key={keyword}>{keyword}</Tag>))}</Item>
        <Item label={t('model.detail.label.framework')}>{model.parameters?.network} </Item>
        <Item label={t('model.detail.label.backbone')}>{model.parameters?.backbone}</Item>
        <Item label={t('dataset.column.create_time')}>{format(model.create_datetime)}</Item>
        <Item>
          <Link to={`/home/model/detail/${model.id}`}>{t('dataset.action.detail')}</Link>
        </Item>
      </Descriptions>
    ) : null
  }

  function renderInfo() {
    return (
      <Card bordered={false} title={<><JiedianIcon />{t("common.history.node.title")} </>} headStyle={{ padding: 0 }} bodyStyle={{ padding: 0 }}>
        {selectedNode.type === HISTORYNODETYPES.DATASET ? renderDataset() : renderModel()}
      </Card>
    )
  }

  return (
    <div className={styles.history}>
      <Breadcrumbs />
      <Card title={renderTitle}>
      <Row wrap={false}>
        <Col flex={'320px'}>
          {renderInfo()}
        </Col>
        <Col flex={1}>
          {cavasHeight && netData.nodes.length ? renderGraph() : null}
        </Col>
      </Row>
      </Card>
    </div>
  )
}

const actions = (dispatch) => {
  return {
    getHistory(type, id) {
      return dispatch({
        type: 'common/getHistory',
        payload: {
          type,
          id,
        }
      })
    },
    getDataset(id) {
      return dispatch({
        type: 'dataset/getDataset',
        payload: id,
      })
    },
    getModel(id) {
      return dispatch({
        type: 'model/getModel',
        payload: id,
      })
    },
  }
}

export default connect(null, actions)(History)