import { A, useNavigate, type RouteSectionProps } from "@solidjs/router"
import { Show, Suspense, createRenderEffect, createResource, type Component } from "solid-js"
import storage from "~/storage"
import { request } from "~/utils"
import styles from "./layout.module.css"
import { ProfileCtx, Role, defaultProfile, getProfile, type Profile } from "./profile"

const Layout: Component<RouteSectionProps> = props => {
  const navigate = useNavigate()
  const username = storage.username
  const token = storage.token
  createRenderEffect(() => {
    if (typeof token == "undefined") {
      navigate("/")
    }
  })
  const [profile, { refetch }] = createResource<Profile>(async () => {
    if (typeof token == "undefined") return defaultProfile
    try {
      return await getProfile(username!, token)
    } catch(err) {
      alert(err)
      delete storage.token
      navigate("/")
      return defaultProfile
    }
  }, {
    initialValue: defaultProfile
  })
  return <Suspense><ProfileCtx.Provider value={[profile, refetch]}>
    <div class={styles.dashboard}>
      <nav>
        <h1>智慧农场</h1>
        <A href="/dashboard">信息概览</A>
        <A href="/dashboard/profile">个人资料</A>
        <Show when={profile().role == Role.FARMER}>
          <A href="/dashboard/farm">农场管理</A>
          <A href="/dashboard/breed">品种管理</A>
          <A href="/dashboard/production">生产管理</A>
          <A href="/dashboard/warehouse">仓库管理</A>
          <A href="/dashboard/stock">库存管理</A>
          <A href="/dashboard/sales">销售管理</A>
          <A href="/dashboard/order">订单管理</A>
        </Show>
        <Show when={profile().role == Role.CUSTOMER}>
          <A href="/dashboard/market">直销市场</A>
          <A href="/dashboard/order">订单管理</A>
        </Show>
        <div class={styles.navBottom}>
          <button onclick={() => {
            // this don't have to be awaited
            request("/logout", {
              body: JSON.stringify({
                "person_name": username
              })
            })
            delete storage.token
            navigate("/")
          }}>登出</button>
        </div>
      </nav>
      <main>
        {props.children}
      </main>
    </div>
  </ProfileCtx.Provider></Suspense>
}

export default Layout
