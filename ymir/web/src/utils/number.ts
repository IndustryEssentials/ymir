
export function humanize(num: number | string) {
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
export function randomBetween(n: number, m: number, exclude: number): number {
  const result = Math.min(m, n) + Math.floor(Math.random() * Math.abs(m - n))

  if (result === exclude) {
    return randomBetween(n, m, exclude)
  }
  return result
}

export const toFixed = (value: number, len: number = 0) => {
  let s = value + ""
  if (s.indexOf(".") == -1) s += "."
  s += new Array(len + 1).join("0")
  const reg = new RegExp("^(-|\\+)?(\\d+(\\.\\d{0," + (len + 1) + "})?)\\d*$")
  const res = s.match(reg)
  if (reg.test(s) && res) {
    let s = '0' + res[2]
    let pm = res[1] || ''
    let a = res[3].length
    let b = true
    if (a == len + 2) {
      let tar = ''
      let c = s.match(/\d/g)
      if (c) {
        const result = c.map(item => Number(item))

        if (parseInt(c[c.length - 1]) > 4) {
          for (var i = c.length - 2; i >= 0; i--) {
            result[i] = parseInt(c[i]) + 1;
            if (result[i] === 10) {
              result[i] = 0
              b = i != 1
            } else break
          }
          tar = result.join('')
        } else {
          tar = (c || []).join('')
        }
        s = tar.replace(new RegExp("(\\d+)(\\d{" + len + "})\\d$"), "$1.$2")
      }
    }

    if (b) s = s.substring(1)
    return (pm + s).replace(/\.$/, "")
  }
  return value + ""
}

export const percent = (num: number, keep = 2) => {
  return toFixed(num * 100.0, keep) + '%'
}

export function isNumber(x: any): x is number {
  return typeof x === "number"
}
