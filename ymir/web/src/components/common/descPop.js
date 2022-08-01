export const DescPop = ({ description }) => {
    const text = description.split(/\n/)
    return <div style={{ maxWidth: '30vw' }}>{text.map((txt, i) =><div key={i}>{txt}</div>)}</div>
}