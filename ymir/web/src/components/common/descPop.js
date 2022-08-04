export const DescPop = ({ description = '', ...rest }) => {
    const text = description.split(/\n/)
    return <div {...rest}>{text.map((txt, i) =><div key={i}>{txt}</div>)}</div>
}