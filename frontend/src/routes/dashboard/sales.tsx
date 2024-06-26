import { createResource, useContext, type Component } from "solid-js"
import { DataTable } from "~/components/DataTable"
import { SegmentedButton, SegmentedButtonSegment } from "~/components/SegmentedButton"
import { handleError, request } from "~/utils"
import { ProfileCtx } from "./profile"

export enum Kind {
  FRUIT = 1, VEGETABLE = 2, DAIRY = 3, MEAT = 4
}

export interface Product {
  id: number
  farmer: string
  name: string
  kind: Kind
  price: number
  stock: number
  info: string
}

export async function getProducts(token: string) {
  const resp = await request("/query_my_product", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["products"] as any[]).map(product => ({
    id: product["product_id"],
    name: product["product_name"],
    kind: product["product_type"],
    price: product["product_price"],
    stock: product["product_num"],
    info: product["product_info"]
  } as Omit<Product, "farmer">))
}

async function updateProduct(token: string, product: Omit<Product, "id" | "farmer">, id?: number) {
  const resp = await request(
    typeof id == "number" ? "/update_product" : "/add_product",
    {
      body: JSON.stringify({
        "log_token": token,
        "product_id": id ?? null,
        "product_name": product.name,
        "product_type": product.kind,
        "product_price": product.price,
        "product_num": product.stock,
        "product_info": product.info
      })
    }
  )
  await handleError(resp)
}

async function deleteProduct(token: string, id: number) {
  const resp = await request("/delete_product", {
    body: JSON.stringify({
      "log_token": token,
      "product_id": id,
    })
  })
  await handleError(resp)
}

const Sales: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [products, { refetch }] = createResource(
    profile,
    profile => getProducts(profile.token),
    { initialValue: [] }
  )
  return <div>
    <h1 style={{ "margin-bottom": "1rem" }}>销售管理</h1>
    <DataTable data={products()}
      head={{
        name: "名称",
        kind: "类型",
        price: "价格",
        stock: "库存",
        info: "详情"
      }}
      cell={{
        name: x => x,
        kind: x => ["水果", "蔬菜", "奶制品", "肉制品"][x],
        price: x => `￥${x}`,
        stock: x => x,
        info: x => x
      }}
      edit={{
        kind: (id, value) => <SegmentedButton type="radio" id={id} name={id} required>
          <SegmentedButtonSegment value={Kind.FRUIT} checked={value == Kind.FRUIT}>水果</SegmentedButtonSegment>
          <SegmentedButtonSegment value={Kind.VEGETABLE} checked={value == Kind.VEGETABLE}>蔬菜</SegmentedButtonSegment>
          <SegmentedButtonSegment value={Kind.DAIRY} checked={value == Kind.DAIRY}>乳制品</SegmentedButtonSegment>
          <SegmentedButtonSegment value={Kind.MEAT} checked={value == Kind.MEAT}>肉制品</SegmentedButtonSegment>
        </SegmentedButton>,
        price: (id, value) => <span attr:with-unit="true">
          <input type="number" name={id} id={id} value={value} min={0} required />
          元
        </span>,
        stock: (id, value) =>
          <input type="number" name={id} id={id} value={value} min={0} step={1} required />,
      }}
      save={async (input, row) => {
        await updateProduct(profile().token, {
          name: input.name,
          kind: Number(input.kind),
          price: Number(input.price),
          stock: Number(input.stock),
          info: input.info
        }, row?.id)
        refetch()
      }}
      remove={async row => {
        await deleteProduct(profile().token, row.id)
        refetch()
      }}
      default={{
        name: "",
        kind: Kind.FRUIT,
        price: 0,
        stock: 0,
        info: ""
      }} />
  </div>
}

export default Sales
