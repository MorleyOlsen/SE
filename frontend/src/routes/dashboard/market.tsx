import { useNavigate, useParams } from "@solidjs/router"
import { For, Show, Suspense, createResource, createUniqueId, useContext, type Component } from "solid-js"
import { handleError, request } from "~/utils"
import styles from "./market.module.css"
import { ProfileCtx } from "./profile"
import { Product } from "./sales"

export async function getProducts(token: string) {
  const resp = await request("/query_all_product", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["products"] as any[]).map(product => ({
    id: product["product_id"],
    farmer: product["seller_name"],
    name: product["product_name"],
    kind: product["product_type"],
    price: product["product_price"],
    stock: product["product_num"],
    info: product["product_info"]
  } as Product))
}

export const Market: Component = () => {
  const navigate = useNavigate()
  const [profile] = useContext(ProfileCtx)
  const [products] = createResource(
    profile,
    profile => getProducts(profile.token),
    { initialValue: [] }
  )
  return <div>
    <h1>直销市场</h1>
    <div class={styles.grid}>
      <Suspense fallback={"加载中……"}>
        <For each={products()}>{product =>
          <div tabindex="0"
            onclick={() => navigate(product.id.toString())}
          >
            <div class={styles.name}>{product.name}</div>
            <div class={styles.seller}>商家：{product.farmer}</div>
            <div>{product.info}</div>
            <div class={styles.price}>￥{product.price}</div>
          </div>
        }</For>
      </Suspense>
    </div>
  </div>
}

async function createOrder(token: string, product: number, amount: number) {
  const resp = await request(
    "/add_invoice",
    {
      body: JSON.stringify({
        "log_token": token,
        "product_id": product,
        "invoice_num": amount
      })
    }
  )
  await handleError(resp)
}

export const MarketItem: Component = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [profile] = useContext(ProfileCtx)
  const [product] = createResource(
    profile,
    async profile => (await getProducts(profile.token))
      .find(product => product.id == Number(id))
  )
  const ids = Array.from({ length: 1 }, () => createUniqueId())
  return <div class={styles.item}>
    <Suspense fallback={<h1>加载中……</h1>}>
      <Show when={product()} fallback={<h1>找不到商品</h1>}>{product => <>
        <h1>{product().name}</h1>
        <div class={styles.seller}>商家：{product().farmer}</div>
        <div class={styles.priceStock}>
          <div class={styles.price}>￥{product().price}</div>
          <div class={styles.stock}>剩余 {product().stock} 件</div>
        </div>
        <form onsubmit={async event => {
          event.preventDefault()
          await createOrder(
            profile().token,
            product().id,
            (event.currentTarget.querySelector(`#${ids[0]}`) as HTMLInputElement).valueAsNumber
          )
          navigate("/dashboard/order")
        }}>
          <label for={ids[0]}>数量</label>
          <input type="number" name={ids[0]} id={ids[0]}
            min="1" max={product().stock} step="1"
            value="1" required
          />
          <button type="submit">购买</button>
        </form>
        <h2>商品详情</h2>
        <div class={styles.details}>{product().info}</div>
      </>}</Show>
    </Suspense>
  </div>
}
