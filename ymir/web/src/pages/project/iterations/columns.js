import t from '@/utils/t'
import { Popover, Tooltip } from 'antd'
import { Link } from 'umi'

import { humanize } from "@/utils/number"
import { validDataset } from '@/constants/dataset'
import { diffTime } from '@/utils/date'
import { getRecommendStage, validModel } from '@/constants/model'

import { DescPop } from "@/components/common/descPop"
import TypeTag from "@/components/task/typeTag"
import RenderProgress from "@/components/common/progress"

function showTitle(str) {
  return <strong>{t(str)}</strong>
}

  const nameCol = {
    title: showTitle("dataset.column.name"),
    key: "name",
    dataIndex: "versionName",
    render: (name, { id, name: groupName, projectId: pid, description }) => {
      const popContent = <DescPop description={description} style={{ maxWidth: '30vw' }} />
      const content = <Link to={`/home/project/${pid}/dataset/${id}`}>{groupName} {name}</Link>
      return description ? <Popover title={t('common.desc')} content={popContent}>
        {content}
      </Popover> : content
    },
    ellipsis: true,
  }
  const sourceCol = {
    title: showTitle("dataset.column.source"),
    dataIndex: "taskType",
    render: (type) => <TypeTag type={type} />,
    sorter: (a, b) => a.taskType - b.taskType,
    ellipsis: true,
  }
  const countCol = {
    title: showTitle("dataset.column.asset_count"),
    dataIndex: "assetCount",
    render: (num) => humanize(num),
    sorter: (a, b) => a.assetCount - b.assetCount,
    width: 120,
  }
  const keywordCol = {
    title: showTitle("dataset.column.keyword"),
    dataIndex: "keywords",
    render: (_, record) => {
      const { gt, pred, } = record
      const renderLine = (keywords, label = t('annotation.gt')) => <div>
        <div>{label}:</div>
        {t('dataset.column.keyword.label', {
          keywords: keywords.join(', '),
          total: keywords.length
        })}
      </div>
      const label = <>{renderLine(gt.keywords)}{renderLine(pred.keywords, 'prediction')}</>
      return validDataset(record) ? <Tooltip title={label}
        color='white' overlayInnerStyle={{ color: 'rgba(0,0,0,0.45)', fontSize: 12 }}
        mouseEnterDelay={0.5}
      ><div>{label}</div></Tooltip> : null
    },
    ellipsis: {
      showTitle: false,
    },
  }
  const stateCol = {
    title: showTitle('dataset.column.state'),
    dataIndex: 'state',
    render: (state, record) => RenderProgress(state, record),
  }
  const createTimeCol = {
    title: showTitle("dataset.column.create_time"),
    dataIndex: "createTime",
    sorter: (a, b) => diffTime(a.createTime, b.createTime),
    sortDirections: ['ascend', 'descend', 'ascend'],
    defaultSortOrder: 'descend',
    width: 180,
  }

  const stageCol = {
      title: showTitle("model.column.stage"),
      dataIndex: "recommendStage",
      render: (_, record) => {
        const stage = getRecommendStage(record)
        return validModel(record) ?
        <div>{stage.name}</div> : null 
      },
      width: 300,
    }
  
const getColumns = (type) => {
  const maps = {
    dataset: [nameCol, sourceCol, countCol, keywordCol, stateCol, createTimeCol],
    model: [nameCol, stageCol, sourceCol, stateCol, createTimeCol],
  }
  return maps[type]
}

export default getColumns
