// // deferred promise
// const deferred = {}
// deferred.promise = new Promise((resolve, reject) => {
//   deferred.resolve = resolve
//   deferred.reject = reject
// })

// // umeng apis
// const methods = [
//   "trackPageview", // http://open.cnzz.com/a/api/trackpageview/
//   "trackEvent", // http://open.cnzz.com/a/api/trackevent/
//   "setCustomVar", // http://open.cnzz.com/a/api/setcustomvar/
//   "setAccount", // http://open.cnzz.com/a/api/setaccount/
//   "setAutoPageview", // http://open.cnzz.com/a/api/setautopageview/
//   "deleteCustomVar", // http://open.cnzz.com/a/api/deletecustomvar/
// ]
// const Umeng = function () {}
// Umeng.prototype = {
//   _cache: [],
//   _resolve() {
//     deferred.resolve()
//   },
//   _reject() {
//     deferred.reject()
//   },
//   _push() {
//     this.debug(arguments)
//     if (window._czc) {
//       window._czc.push.apply(window._czc, arguments)
//     } else {
//       this._cache.push.apply(this._cache, arguments)
//     }
//   },
//   _createMethod(method) {
//     return function () {
//       const args = Array.prototype.slice.apply(arguments)
//       this._push([`_${method}`, ...args])
//     }
//   },
//   debug() {},
//   ready() {
//     return deferred.promise
//   },
//   install(options) {
//     if (!window) {
//       return
//     }
//     if (this.installed) return

//     if (options.debug) {
//       this.debug = console.debug
//     } else {
//       this.debug = () => {}
//     }

//     let siteId = null
//     // passsing siteId through object or string
//     if (typeof options === "object") {
//       siteId = options.siteId
//       if (options.autoPageview !== false) {
//         options.autoPageview = true
//       }
//     } else {
//       siteId = options
//     }
//     if (!siteId) {
//       return console.error("siteId is missing")
//     }
//     this.installed = true

//     // insert u-web statistics script
//     const script = document.createElement("script")
//     const src = `https://s11.cnzz.com/z_stat.php?id=${siteId}&web_id=${siteId}`
//     script.src = options.src || src

//     // callback when the script is loaded
//     script.onload = () => {
//       // if the global object is exist, resolve the promise, otherwise reject it
//       if (window._czc) {
//         this._resolve()
//       } else {
//         console.error(
//           "loading umeng statistics script failed, please check src and siteId"
//         )
//         return this._reject()
//       }
//       // load from cache
//       this._cache.forEach((cache) => {
//         window._czc.push(cache)
//       })
//       this._cache = []
//     }

//     this.setAccount(options.siteId)
//     this.setAutoPageview(options.autoPageview)

//     document.body.appendChild(script)
//   },
//   patch(method) {
//     this[method] = this._createMethod(method)
//   },
// }

// const umeng = new Umeng()

// const options = {
//   siteId: "1280069634",
//   autoPageview: false,
// }

// // apis
// methods.forEach((method) => (umeng[method] = umeng._createMethod(method)))

// // umeng.install(options)

// export default umeng
