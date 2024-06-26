import { For, Show, createResource, useContext, type Component } from "solid-js"
import styles from "~/components/DataTable.module.css"
import { Bool, handleError, request } from "~/utils"
import { ProfileCtx, Role } from "./profile"

interface Order {
  id: number
  customer: string
  customerAddress: string
  customerPhone: string
  seller: string
  sellerAddress: string
  sellerPhone: string
  product: string
  amount: number
  subtotal: number
  time: Date
  sent: Bool
}

export async function getOrders(token: string) {
  const resp = await request("/query_my_invoice", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["invoices"] as any[]).map(order => ({
    id: order["invoice_id"],
    customer: order["buyer_name"],
    customerAddress: order["buyer_address"],
    customerPhone: order["buyer_phone"],
    seller: order["seller_name"],
    sellerAddress: order["seller_address"],
    sellerPhone: order["seller_phone"],
    product: order["product_name"],
    amount: order["invoice_num"],
    subtotal: order["invoice_money"],
    time: new Date(order["invoice_time"]),
    sent: order["invoice_out"]
  } as Order))
}

async function updateOrderSent(token: string, id: number, sent: Bool) {
  const resp = await request(
    "/update_invoice",
    {
      body: JSON.stringify({
        "log_token": token,
        "invoice_id": id,
        "invoice_out": sent
      })
    }
  )
  await handleError(resp)
}

const Order: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [orders, { refetch }] = createResource(
    profile,
    profile => getOrders(profile.token),
    { initialValue: [] }
  )
  return <div>
    <h1 style={{ "margin-bottom": "1rem" }}>销售管理</h1>
    <table class={styles.dataTable}>
      <thead>
        <tr>
          <th>商品名</th>
          <Show when={profile().role == Role.FARMER}>
            <th>顾客</th>
            <th>收货地址</th>
          </Show>
          <Show when={profile().role == Role.CUSTOMER}>
            <th>卖家</th>
            <th>发货地址</th>
          </Show>
          <th>数量</th>
          <th>金额</th>
          <th>下单时间</th>
          <th>已发货</th>
        </tr>
      </thead>
      <tbody>
        <For each={orders()}>{order =>
          <OrderRow order={order} refetch={refetch} />
        }</For>
      </tbody>
    </table>
  </div>
}

const OrderRow: Component<{
  order: Order,
  refetch(): void,
}> = props => {
  const [profile] = useContext(ProfileCtx)
  return <tr>
    <td>{props.order.product}</td>
    <Show when={profile().role == Role.FARMER}>
      <td>{props.order.customer}</td>
      <td>{props.order.customerPhone} {props.order.customerAddress}</td>
    </Show>
    <Show when={profile().role == Role.CUSTOMER}>
      <td>{props.order.seller}</td>
      <td>{props.order.sellerPhone} {props.order.sellerAddress}</td>
    </Show>
    <td>{props.order.amount}</td>
    <td>￥{props.order.subtotal}</td>
    <td>{props.order.time.toLocaleString("zh-CN", {
      "dateStyle": "short",
      "timeStyle": "short"
    })}</td>
    <td>
      {"否是"[props.order.sent]}
      {" "}
      <a onclick={async () => {
        await updateOrderSent(
          profile().token,
          props.order.id,
          1 - props.order.sent
        )
        props.refetch()
      }}>切换</a>
    </td>
  </tr>
}

export default Order
