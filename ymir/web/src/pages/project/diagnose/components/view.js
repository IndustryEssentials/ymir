const View = (Component) => {
  const Viewer = (props) => {
    return <Component {...props} />
  }
  return Viewer
}

export default View
