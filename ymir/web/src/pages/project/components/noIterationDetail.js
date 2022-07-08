import { Col, Row, Space } from "antd"
import { Link } from "umi"
import t from "@/utils/t"
import s from "../detail.less"
import { EditIcon,  EyeOffIcon } from "@/components/common/icons"
import { TestingSet } from "./testingSet"

const NoIterationDetail = ({ project }) => {
  return (<>
      <Row>
        <Col flex={1}>
          <Space className={s.detailPanel} wrap>
            <span className={s.name}>{project.name}</span>
            <span>{t('project.train_classes')}: <span className={s.black}>{project?.keywords?.join(',')}</span></span>
            {project.description ? <span>{t('project.detail.desc')}: {project.description}</span> : null}
          </Space>
        </Col>
        <Col>
          <Space>
            <Link to={`/home/project/${project.id}/add`}><EditIcon /><span>{t('project.settings.title')}</span></Link>
            <Link to={`/home/project/${project.id}/hidden`}><EyeOffIcon /><span>{t('common.hidden.list')}</span></Link>
          </Space>
        </Col>
      </Row>
      <TestingSet project={project} />
    </>
  )
}

export default NoIterationDetail
