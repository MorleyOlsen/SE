import { API_ROOT } from "./config"

export type MaybePromise<T> = Promise<T> | T

export enum Bool {
  FALSE, TRUE
}

export async function handleError(resp: Response) {
  if (!resp.ok) {
    try {
      const { error } = await resp.json()
      throw `错误：${error}`
    } catch (err) {
      if (typeof err == "string") {
        throw err
      } else {
        throw `未知错误`
      }
    }
  }
}

export function request(path: string, options: RequestInit = {}) {
  return fetch(new URL(path, API_ROOT), {
    method: "post",
    mode: "cors",
    redirect: "follow",
    referrerPolicy: "no-referrer",
    headers: {
      "Content-Type": "application/json"
    },
    ...options
  })
}
