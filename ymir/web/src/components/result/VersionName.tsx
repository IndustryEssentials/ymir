import React from "react"
import { Result } from "@/interface/common"

type Props = { result: Result, extra?: React.ReactElement | string }
const VersionName: React.FC<Props> = ({ result, extra }) => {
    const { name, versionName } = result || {}
    const label = `${name} ${versionName}`
    return <span className='versionName' title={label}>{label} {extra}</span>
}

export default VersionName
