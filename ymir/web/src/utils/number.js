export function numFormat(num) {
  if (typeof num !== "number") {
    return num
  }
  return num
}

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
 * get a random number between given range
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
  if (result < 0) {
    return 0
  }
  return result
}
