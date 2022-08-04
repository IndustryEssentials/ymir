import { Descriptions, Tag } from "antd"
import t from '@/utils/t'
import { FIELDS, getConfigUrl, isLiveCode } from "@/pages/task/components/liveCodeConfig"

export default (config = {}) => {
  const configUrl = getConfigUrl(config)
  const fields = FIELDS.map(({ key, field }, index) => ({
    label: `task.train.live.${key}`,
    key: field,
    extra: index === FIELDS.length - 1 ? <a href={configUrl} target='_blank'>{t('common.view')}</a> : null,
  }))
  const typeLabel = isLiveCode(config) ? 'live' : 'local'
  const typeItem = <Descriptions.Item label={t('task.detail.label.function')}>{t(`task.detail.function.${typeLabel}`)}</Descriptions.Item>
  return <>
    {typeItem}
    {isLiveCode(config) ? fields.map(({ label, key, extra }) => (
      <Descriptions.Item key={key} label={t(label)}>
        {config[key]} {extra}
      </Descriptions.Item>
    )) : null}
  </>
}
