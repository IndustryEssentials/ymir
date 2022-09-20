import { List, Skeleton, Space, Col, Row, Popover } from "antd"
import t from "@/utils/t"
import s from "./list.less"
import { useHistory } from "umi"
import { getStageLabel } from '@/constants/iteration'
import KeywordsItem from "./keywordsItem"

export const Lists = ({ projects = [], more = '' }) => {
  const history = useHistory()
  const renderItem = (item) => {
    const title = <Row wrap={false} className='title'>
      <Col flex={1}>
        <Space>
          <span className={s.name}>{item.name} {item.isExample ? <span className="nameExtra">{t('project.example')}</span> : null}</span>
          <span className='titleItem'>
            <span className='titleLabel'>{t('project.train_classes')}:</span>
            <span className='titleContent'><KeywordsItem keywords={item.keywords} /></span>
          </span>
          {item.enableIteration ? <span className='titleItem'>
            <span className='titleLabel'>{t('project.iteration.current')}:</span>
            <span className='titleContent emphasis'>{t(getStageLabel(item.currentStage, item.round))}</span>
          </span> : null }
        </Space>
      </Col>
      <Col>{more}</Col>
    </Row>

    const tipContent = <div>
      <div>{t('project.train_set')}: {item.trainSet?.name}</div>
      <div>{t('project.test_set')}: {item.testSet?.name}</div>
      <div>{t('project.mining_set')}: {item.miningSet?.name}</div>
    </div>;
    
    const desc = <>
      <Row className='content' justify="center">
        <Col span={5} className={s.stats}>
          <div className='contentLabel'>{t('project.tab.set.title')}</div>
          <div className='contentContent'>{item.setCount}</div>
        </Col>
        <Col span={5} className={s.stats}>
          <div className='contentLabel'>{t('project.tab.model.title')}</div>
          <div className='contentContent'>{item.modelCount}</div>
        </Col>
        <Col span={9} className={s.stats}>
          <div className='contentLabel'>{t('project.train_set')}|{t('project.test_set')}|{t('project.mining_set')}</div>
          <div className='sets'>
            <Popover placement='right' content={tipContent}>
              <span className='setLabel'>{item.trainSet?.name}</span><span>|</span>
              <span className='setLabel'>{item.testSet?.name}</span><span>|</span>
              <span className='setLabel'>{item.miningSet?.name}</span>
            </Popover>
          </div>
        </Col>
    
        {item.enableIteration ? <Col span={5} className={s.stats}>
          <div className='contentLabel'>{t('project.iteration.number')}</div>
          <div className='contentContent'><span className='currentIteration'>{item.round}</span></div>
        </Col> : null }
      </Row>
      <Row>
        <Col flex={1}><span className='bottomLabel'>{t('project.content.desc')}:</span> <span className={s.bottomContent}>{item.description}</span></Col>
        <Col><span className='bottomContent'>{item.createTime}</span></Col>
      </Row>
    </>

    return <List.Item 
      onClick={() => { history.push(`/home/project/${item.id}/detail`) }}>
      <Skeleton active loading={item.loading}>
        <List.Item.Meta title={title} description={desc}>
        </List.Item.Meta>
      </Skeleton>
    </List.Item>
  }
  return (
    <List
      className='list'
      dataSource={projects}
      renderItem={renderItem}
    />
  )
}
