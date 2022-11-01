import React from "react"
type Props = {
    description: string,
    [key: string]: any,
}
export const DescPop: React.FC<Props> = ({ description = '', ...rest }) => {
    const text = description.split(/\n/)
    return <div {...rest}>
        {text.map((txt, i) => <div key={i}>{txt}</div>)}
    </div>
}