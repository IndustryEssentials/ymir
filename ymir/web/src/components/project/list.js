import { List, Skeleton, Space, Col, Row, Popover } from "antd"
import t from "@/utils/t"
import s from "./list.less"
import { useHistory } from "umi"

export const Lists = ({ projects=[], more=''}) => {
  const history = useHistory()
  const renderItem = (item) => {
    const title = <Row wrap={false} className={s.title}>
      <Col flex={1}>
        <Space>
          <span className={s.name}>{item.name}</span>
          <span className={s.titleItem}><span className={s.titleLabel}>{t('project.train_classes')}:</span><span className={s.titleContent}>{item.keywords.join(',')}</span></span>
          <span className={s.titleItem}><span className={s.titleLabel}>{t('project.target.map')}:</span><span className={s.titleContent}>{item?.targetMap}%</span></span>
          <span className={s.titleItem}><span className={s.titleLabel}>{t('project.iteration.current')}:</span><span className={s.titleContent}>{item?.currentIteration?.currentStage}</span></span>
        </Space>
      </Col>
      <Col>{more}</Col>
    </Row>
    const tipContent = <div>
      <div>{t('project.train_set')}：{item.trainSet?.name}</div>
      <div>{t('project.test_set')}：{item.testSet?.name}</div>
      <div>{t('project.mining_set')}：{item.miningSet?.name}</div>
    </div>;
    const desc = <>
      <Row className={s.content} justify="center">
        <Col span={5} className={s.stats}>
          <div className={s.contentLabel}>Datasets</div>
          <div className={s.contentContent}>{item.setCount}</div>
        </Col>
        <Col span={5} className={s.stats}>
          <div className={s.contentLabel}>Models</div>
          <div className={s.contentContent}>{item.modelCount}</div>
        </Col>
        <Col span={9} className={s.stats}>
          <div className={s.contentLabel}>{t('project.train_set')}|{t('project.test_set')}|{t('project.mining_set')}</div>
            <div className={s.sets}>
              <Popover placement = 'right' content={tipContent}>
                <span className={s.setLabel}>{item.trainSet?.name}</span><span>|</span>
                <span className={s.setLabel}>{item.testSet?.name}</span><span>|</span>
                <span className={s.setLabel}>{item.miningSet?.name}</span>
              </Popover>
            </div>
        </Col>
        <Col span={5} className={s.stats}>
          <div className={s.contentLabel}>{t('project.iteration.number')}</div>
          <div className={s.contentContent}><span className={s.currentIteration}>{item?.currentIteration?.iterationRound}</span>/{item?.targetIteration}</div>
        </Col>
      </Row>
      <Row>
        <Col flex={1}><span className={s.bottomLabel}>{t('project.content.desc')}:</span> <span className={s.bottomContent}>{item.description}</span></Col>
        <Col><span className={s.bottomContent}>{item.createTime}</span></Col>
      </Row>
    </>

    return <List.Item className={item.state ? 'success' : 'failure'}
            onClick={() => { history.push(`/home/project/detail/${item.id}`) }}>
      <Skeleton active loading={item.loading}>
        <List.Item.Meta title={title} description={desc}>
        </List.Item.Meta>
      </Skeleton>
    </List.Item>
  }
  return (
    <List
      className={s.list}
      dataSource={projects}
      renderItem={renderItem}
    />
  )
}
