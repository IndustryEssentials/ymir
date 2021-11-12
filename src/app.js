import umeng from "./services/umeng"

export const dva = {
  config: {
    onError(err) {
      err.preventDefault()
      console.error(err.message)
    },
  },
}

export const onRouteChange = ({ routes, matchedRoutes, location, action }) => {
  //change document.title
  // console.log("onRouteChange", location, routes, matchedRoutes, action)
  // umeng.trackPageview(matchedRoutes.lastItem.route.path)
  // umeng.ready().then(() => {
  //   console.log(window._czc, umeng)
  // })
}
