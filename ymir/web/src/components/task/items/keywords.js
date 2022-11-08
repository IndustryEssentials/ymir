import { Descriptions, Tag } from "antd"
import t from '@/utils/t'

export default (keywords = []) => (
  <Descriptions.Item label={t("task.detail.label.train_goal")}>
    {keywords.map((keyword) => <Tag key={keyword}>{keyword}</Tag>)}
  </Descriptions.Item>
)
