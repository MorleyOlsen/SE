import { Component, For, Show, Suspense, createResource, useContext } from "solid-js"
import { handleError, request } from "~/utils"
import { getBreeds } from "./breed"
import { getFarms } from "./farm"
import styles from "./index.module.css"
import { ProfileCtx, Role } from "./profile"
import { getProducts } from "./sales"
import { getWarehouses } from "./warehouse"

const Index: Component = () => {
  const [profile] = useContext(ProfileCtx)
  return <div class={styles.root}>
    <h1>{{
      [Role.FARMER]: "农场主",
      [Role.CUSTOMER]: "顾客"
    }[profile().role]} <em>{profile().name}</em>，欢迎来到智慧农场</h1>
    <div>
      <Show when={profile().role == Role.FARMER}>
        <Messages />
        <HarvestStatus />
        <ExpiryNotice />
      </Show>
      <Show when={profile().role == Role.CUSTOMER}>
        <SendMessage />
      </Show>
    </div>
  </div>
}

export default Index

async function getMessages(token: string) {
  const resp = await request("/query_all_messages", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["messages"] as any[]).map(message => ({
    content: message["message_info"] as string,
    time: new Date(message["message_time"])
  }))
}

const Messages: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [messages] = createResource(
    profile,
    profile => getMessages(profile.token),
    { initialValue: [] }
  )
  return <Suspense>
    <Show when={messages().length > 0}>
      <section>
        <div>您收到了 <em>{messages().length}</em> 条顾客的留言：</div>
        <For each={messages()}>{msg =>
          <div class={styles.message}>
            {msg.content}
            <time datetime={msg.time.toISOString()}>
              {msg.time.toLocaleString("zh-CN", {
                "dateStyle": "short",
                "timeStyle": "short"
              })}
            </time>
          </div>
        }</For>
      </section>
    </Show>
  </Suspense>
}

function dateAddDays(date: Date, days: number) {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

async function getHarvestStatuses(token: string) {
  const farms = await getFarms(token)
  const breeds = await getBreeds(token)
  const resp = await request("/expiry_info", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["mature_batches"] as any[]).map(production => {
    const breed = breeds.find(breed => breed.id == production["type_id"])!
    return {
      farm: farms.find(farm => farm.id == production["farm_id"])!.name,
      breed: breed!.name,
      time: dateAddDays(new Date(production["batch_start"]), breed.period)
    }
  })
}

const HarvestStatus: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [messages] = createResource(
    profile,
    profile => getHarvestStatuses(profile.token),
    { initialValue: [] }
  )
  return <Suspense>
    <Show when={messages().length > 0}>
      <section>
        <div>您有 <em>{messages().length}</em> 处农田/养殖场需要收获：</div>
        <For each={messages()}>{msg =>
          <div class={styles.message}>
            {msg.farm} 的 {msg.breed}
            <time datetime={msg.time.toISOString()}>
              {msg.time.toLocaleString("zh-CN", {
                "dateStyle": "short",
                "timeStyle": "short"
              })}
            </time>
          </div>
        }</For>
      </section>
    </Show>
  </Suspense>
}

async function getExpiryNotices(token: string) {
  const warehouses = await getWarehouses(token)
  const products = await getProducts(token)
  const resp = await request("/expiry_repo_info", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["expire_batches"] as any[]).map(stock => {
    return {
      warehouse: warehouses.find(warehouse => warehouse.id == stock["repo_id"])!.name,
      product: products.find(product => product.id == stock["product_id"])!.name,
      time: dateAddDays(new Date(stock["batchrepo_start"]), stock["batchrepo_period"])
    }
  })
}
const ExpiryNotice: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [messages] = createResource(
    profile,
    profile => getExpiryNotices(profile.token),
    { initialValue: [] }
  )
  return <Suspense>
    <Show when={messages().length > 0}>
      <section>
        <div>您有 <em>{messages().length}</em> 批库存已经过期：</div>
        <For each={messages()}>{msg =>
          <div class={styles.message}>
            {msg.warehouse} 的 {msg.product}
            <time datetime={msg.time.toISOString()}>
              {msg.time.toLocaleString("zh-CN", {
                "dateStyle": "short",
                "timeStyle": "short"
              })}
            </time>
          </div>
        }</For>
      </section>
    </Show>
  </Suspense>
}

async function sendMessage(token: string, message: string) {
  const resp = await request("/add_message", {
    body: JSON.stringify({
      "log_token": token,
      "message_info": message
    })
  })
  await handleError(resp)
}

const SendMessage: Component = () => {
  const [profile] = useContext(ProfileCtx)
  return <section>
    <div>您可以在此发送留言。</div>
    <form onsubmit={async event => {
      event.preventDefault()
      const elem = event.currentTarget.querySelector("textarea") as HTMLTextAreaElement
      await sendMessage(profile().token, elem.value)
      elem.value = ""
    }}>
      <textarea />
      <button type="submit">发送</button>
    </form>
  </section>
}
