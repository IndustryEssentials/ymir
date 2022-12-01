type RleSource = number[][]
type RleResult = string
export function encode(arr: RleSource, h: number) {
  return pipe(arr, flat.bind(undefined, h), unrle, unleb)
}

export function decode(encodedStr: RleResult, h: number) {
  console.log('encodedStr: RleResult, h:', encodedStr, h)
  return pipe(encodedStr, unleb, unrle, flat.bind(undefined, h))
}

export function decodeRle(rleArr: number[], h: number) {
  return pipe(rleArr, unrle, flat.bind(undefined, h))
}

export default { encode, decode, decodeRle }

function flat(h: number, arr: number[]) {
  /** @type {number[][]} */
  const memo: RleSource = []

  for (let i = 0; i < arr.length; i += h) {
    for (let j = 0; j < h; j++) {
      if (!memo[j]) {
        memo[j] = []
      }
      memo[j].push(arr[i + j])
    }
  }

  return memo
}

function unrle(arr: number[]) {
  const memo = []
  let j, k, v = false

  for (j = 0; j < arr.length; j++) {
    for (k = 0; k < arr[j]; k++) {
      memo.push(v ? 1 : 0)
    }
    v = !v
  }

  return memo
}

function unleb(s: string): number[] {
  let m = 0
  let p = 0

  let k: number
  let x: number
  let more = false
  const memo = []

  m = 0

  while (s[p]) {
    x = 0
    k = 0
    more = true
    while (more) {
      const c = s[p].charCodeAt(0) - 48
      x |= (c & 0x1f) << (5 * k)
      more = !!(c & 0x20)
      p++
      k++
      if (!more && c & 0x10) {
        x |= -1 << (5 * k)
      }
    }
    if (m > 2) {
      x += memo[m - 2]
    }
    memo[m++] = x
  }

  return memo
}

function pipe(initialValue: unknown, ...fns: Function[]) {
  return fns.reduce((memo, fn) => fn(memo), initialValue)
}
