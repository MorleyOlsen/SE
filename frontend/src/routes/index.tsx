import { useNavigate } from "@solidjs/router"
import { Show, createRenderEffect, createSignal, createUniqueId, type Component } from "solid-js"
import splash from "~/assets/splash.jpg"
import { SegmentedButton, SegmentedButtonSegment } from "~/components/SegmentedButton"
import storage from "~/storage"
import { handleError, request } from "~/utils"
import { Role } from "./dashboard/profile"
import styles from "./index.module.css"

const Index: Component = () => {
  const [isRegister, setRegister] = createSignal(false)
  return <div class={styles.page}>
    <main>
      <h1>欢迎来到<em>智慧农场</em></h1>
      <Show when={!isRegister()}>
        <p>没有账号？请先<a onclick={() => setRegister(true)}>注册</a>。</p>
      </Show>
      <Show when={isRegister()}>
        <p>已有账号？返回<a onclick={() => setRegister(false)}>登录</a>。</p>
      </Show>
      <Login isRegister={isRegister()} />
    </main>
    <picture>
      <img src={splash} alt="麦田" />
    </picture>
  </div>
}

export default Index

async function register(username: string, password: string, role: Role) {
  const resp = await request("/register", {
    body: JSON.stringify({
      "person_name": username,
      "person_pw": password,
      "role_id": role
    })
  })
  await handleError(resp)
  const { log_token: token } = await resp.json()
  storage.username = username
  storage.token = token
}

async function login(username: string, password: string) {
  const resp = await request("/login", {
    body: JSON.stringify({
      "person_name": username,
      "person_pw": password
    })
  })
  await handleError(resp)
  const { log_token: token } = await resp.json()
  storage.username = username
  storage.token = token
}

const Login: Component<{
  isRegister: boolean
}> = props => {
  const navigate = useNavigate()
  createRenderEffect(() => {
    if (typeof storage.token == "string") {
      navigate("/dashboard")
    }
  })
  const ids = Array.from({ length: 4 }, () => createUniqueId())
  return <form onsubmit={async event => {
    event.preventDefault()
    const elem = event.currentTarget
    const data = new FormData(elem)
    // these are guaranteed to be string by `required`
    const username = data.get(ids[1])! as string
    const password = data.get(ids[2])! as string
    try {
      if (props.isRegister) {
        const role = Number.parseInt(data.get(ids[0])! as string)
        const repeatPassword = data.get(ids[3])! as string
        if (password != repeatPassword) throw "错误：密码不一致"
        await register(username, password, role)
      } else {
        await login(username, password)
      }
      navigate("/dashboard")
    } catch (err) {
      alert(err)
      elem.reset()
      const role = data.get(ids[0])! as string
      if (props.isRegister) (
        elem.querySelector(`#${ids[0]} > input[value="${role}"]`)! as HTMLInputElement
      ).checked = true
    }
  }}>
    <Show when={props.isRegister}>
      <label for={ids[0]}>身份</label>
      <SegmentedButton type="radio" name={ids[0]} id={ids[0]} required>
        <SegmentedButtonSegment value={Role.FARMER} checked>农场主</SegmentedButtonSegment>
        <SegmentedButtonSegment value={Role.CUSTOMER}>顾客</SegmentedButtonSegment>
      </SegmentedButton>
    </Show>
    <label for={ids[1]}>账号</label>
    <input type="text" name={ids[1]} id={ids[1]} required />
    <label for={ids[2]}>密码</label>
    <input type="password" name={ids[2]} id={ids[2]} required />
    <Show when={props.isRegister}>
      <label for={ids[3]} style="margin-left: -2em">重复密码</label>
      <input type="password" name={ids[3]} id={ids[3]} required />
    </Show>
    <button type="submit">{props.isRegister ? "注册" : "登录"}</button>
  </form>
}

