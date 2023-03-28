import { Card, CardProps } from 'antd'
import { CardTabListType } from 'antd/lib/card'
import { FC, ReactNode, useEffect, useState } from 'react'
import { useLocation, useHistory, Location } from 'umi'

type Props = CardProps & {
  data: (CardTabListType & { content: ReactNode })[]
  initialTab?: string
}
const CardTabs: FC<Props> = ({ data = [], initialTab, ...props }) => {
  const location: Location<{ type?: string }> = useLocation()
  const history = useHistory()
  const [tabs, setTabs] = useState<CardTabListType[]>([])
  const [contents, setContents] = useState<{ [key: string]: ReactNode }>({})
  const [active, setActive] = useState('')

  useEffect(() => {
    tabs.length && !active && setActive(initialTab || tabs[0].key)
  }, [tabs])
  useEffect(() => {
    const type = location?.state?.type
    if (typeof type !== 'undefined') {
      setActive(type)
    }
  }, [location.state])

  useEffect(() => {
    setTabs(data.map(({ tab, key }) => ({ tab: tab || key, key })))
    setContents(data.reduce((prev, { content, key }) => ({ ...prev, [key]: content }), {}))
  }, [data])

  return (
    <Card
      className="fullTab"
      {...props}
      tabList={tabs}
      activeTabKey={active}
      onTabChange={(key) => history.replace({ state: { type: key } })}
      tabProps={{
        moreIcon: null,
      }}
    >
      {contents[active]}
    </Card>
  )
}

export default CardTabs
