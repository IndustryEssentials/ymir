
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

export const toFixed = (value, len) => {
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
