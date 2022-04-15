import { useEffect, useState } from "react"
import { setLocale, getLocale } from "umi"
import { EnglishIcon, ChinaIcon } from '@/components/common/icons'

function LangBtn({ dark = false }) {
  const color = dark ? 'rgba(0, 0, 0, 0.45)' : '#fff'
  const [all] = useState([
    { value: "zh-CN", to: 'en-US', label: "English", icon: <ChinaIcon style={{ color, fontSize: 24 }} /> },
    { value: "en-US", to: 'zh-CN', label: "\u4E2D\u6587", icon: <EnglishIcon style={{ color, fontSize: 24 }} /> },
  ])

  const [currentLang, setCurrentLang] = useState(getLocale())
  const [current, setCurrent] = useState(all[0])

  useEffect(() => {
    const current = all.find(lang => lang.value === currentLang) || all[1]
    setLocale(current.value)
    setCurrent(current)
  }, [currentLang])

    return (
      <span
        onClick={() => setCurrentLang(current.to)}
        title={current.label}
        style={{ cursor: 'pointer' }}
      >
        {current.icon}
      </span>
    )
}

export default LangBtn
