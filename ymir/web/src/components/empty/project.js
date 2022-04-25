
import { Button, Space } from 'antd'

import t from '@/utils/t'
import s from './empty.less'
import { NoSjjIcon, ImportIcon, AddIcon } from '@/components/common/icons'
import { useHistory } from 'umi'

const ProjectEmpty = ({ style = {}, addExample = () => {} }) => {
  const history = useHistory()
  
  return (
  <Space className={s.empty} style={style} direction="vertical">
    <NoSjjIcon className={s.primaryIcon} style={{ fontSize: 80 }} />
    <h3>{t("project.empty.label")}</h3>
    <Space className={s.actions}>
      <Button className={s.addBtn} type="primary" onClick={() => history.push('/home/project/add')} icon={<AddIcon />}>{t('project.new.label')}</Button>
      <Button className={s.addBtn} type="primary" onClick={() => addExample()} icon={<AddIcon />}>{t('project.new.example.label')}</Button>
    </Space>
  </Space>
)}

export default ProjectEmpty
