
export function humanize(num) {
  if (!num) {
    return 0
  }
  if (isNaN(Number(num))) {
    return num
  }
  const units = ['', 'K', 'M', 'B']
  num = typeof num == 'string' ? parseFloat(num) : num
  num = num.toLocaleString()
  const ell = num.match(/,/ig)

  return num.replace(/^(\d+)[,]?.*$/, '$1' + units[ell ? ell.length : 0])
}

export function randomNumber(count = 6) {
  const min = Math.pow(10, count - 1), max = Math.pow(10, count) - 1
  const range = max - min
  return min + Math.round(Math.random() * range)
}

/**
 * get a random number between range of [min, max)
 * @param {number} n  min of range 
 * @param {number} m  max of range
 * @param {number} exclude exclude number
 * @returns 
 */
export function randomBetween(n, m, exclude) {
  const result = Math.min(m, n) + Math.floor(Math.random() * Math.abs(m - n))

  if (result === exclude) {
    return randomBetween(n, m, exclude)
  }
  return result
}

const toFixed = (value, len) => {
  var s = value + ""
  if (!len) len = 0
  if (s.indexOf(".") == -1) s += "."
  s += new Array(len + 1).join("0")
  if (new RegExp("^(-|\\+)?(\\d+(\\.\\d{0," + (len + 1) + "})?)\\d*$").test(s)) {
    var s = "0" + RegExp.$2, pm = RegExp.$1, a = RegExp.$3.length, b = true
    if (a == len + 2) {
      a = s.match(/\d/g)
      if (parseInt(a[a.length - 1]) > 4) {
        for (var i = a.length - 2; i >= 0; i--) {
          a[i] = parseInt(a[i]) + 1;
          if (a[i] == 10) {
            a[i] = 0
            b = i != 1
          } else break
        }
      }
      s = a.join("").replace(new RegExp("(\\d+)(\\d{" + len + "})\\d$"), "$1.$2")

    } 
    if (b) s = s.substring(1)
    return (pm + s).replace(/\.$/, "")
  }
  return value + "";

}

export const percent = (num, keep = 2) => {
  return toFixed(num * 100.0, keep) + '%'
}


console.log('hello: ', percent(20.405), 20.405)
console.log('hello: ', percent(20.415), 20.415)
console.log('hello: ', percent(20.425), 20.425)
console.log('hello: ', percent(20.435), 20.435)
console.log('hello: ', percent(20.445), 20.445)
console.log('hello: ', percent(20.455), 20.455)
console.log('hello: ', percent(20.465), 20.465)
console.log('hello: ', percent(20.475), 20.475)
console.log('hello: ', percent(20.485), 20.485)
console.log('hello: ', percent(20.495), 20.495)
console.log('hello: ', percent(0.05), 0.05)
console.log('hello: ', percent(0.15), 0.15)
console.log('hello: ', percent(0.25), 0.25)
console.log('hello: ', percent(0.35), 0.35)
console.log('hello: ', percent(0.45), 0.45)
console.log('hello: ', percent(0.55), 0.55)
console.log('hello: ', percent(0.65), 0.65)
console.log('hello: ', percent(0.75), 0.75)
console.log('hello: ', percent(0.85), 0.85)
console.log('hello: ', percent(0.95), 0.95)
console.log('hello: ', percent(0.0512341234), 0.0512341234)
console.log('hello: ', percent(0.153543455), 0.153543455)
console.log('hello: ', percent(0.2654565), 0.2654565)
console.log('hello: ', percent(0.3067895), 0.3067895)
console.log('hello: ', percent(0.4857545), 0.4857545)
console.log('hello: ', percent(0.59567545), 0.59567545)
console.log('hello: ', percent(0.6457345), 0.6457345)
console.log('hello: ', percent(0.759999), 0.759999)
console.log('hello: ', percent(0.852345), 0.852345)
console.log('hello: ', percent(0.95245235432), 0.95245235432)