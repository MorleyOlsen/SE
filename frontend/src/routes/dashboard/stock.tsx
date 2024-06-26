import { createResource, useContext, type Component } from "solid-js"
import { DataTable } from "~/components/DataTable"
import { DropdownInput } from "~/components/DropdownInput"
import { SegmentedButton, SegmentedButtonSegment } from "~/components/SegmentedButton"
import { Bool, handleError, request } from "~/utils"
import { ProfileCtx } from "./profile"
import { getProducts } from "./sales"
import { getWarehouses } from "./warehouse"

interface Stock {
  id: number
  warehouse: number
  product: number
  begin: Date
  period: number
  amount: number
  remaining: number
  size: number
  shelved: Bool
  expired: Bool
}

export async function getStocks(token: string) {
  const resp = await request("/query_all_repo_batch", {
    body: JSON.stringify({
      "log_token": token
    })
  })
  await handleError(resp)
  const data = await resp.json()
  return (data["repo_batches"] as any[]).map(stock => ({
    id: stock["batchrepo_id"],
    warehouse: stock["repo_id"],
    product: stock["product_id"],
    begin: new Date(stock["batchrepo_start"]),
    period: stock["batchrepo_period"],
    amount: stock["batchrepo_num"],
    remaining: stock["batchrepo_left"],
    size: stock["batchrepo_size"],
    shelved: stock["batchrepo_on"],
    expired: stock["batchrepo_expire"],
    } as Stock))
}

async function updateStock(token: string, stock: Omit<Stock, "id">, id?: number) {
  const resp = await request(
    typeof id == "number" ? "/update_repo_batch" : "/add_repo_batch",
    {
      body: JSON.stringify({
        "log_token": token,
        "batchrepo_id": id ?? null,
        "repo_id": stock.warehouse,
        "product_id": stock.product,
        "batchrepo_start": stock.begin.toISOString(),
        "batchrepo_period": stock.period,
        "batchrepo_size": stock.size,
        "batchrepo_num": stock.amount,
        "batchrepo_left": stock.remaining,
        "batchrepo_on": stock.shelved,
        "batchrepo_expire": stock.expired
      })
    }
  )
  await handleError(resp)
}

const Stock: Component = () => {
  const [profile] = useContext(ProfileCtx)
  const [stocks, { refetch }] = createResource(
    profile,
    profile => getStocks(profile.token),
    { initialValue: [] }
  )
  const [warehouses] = createResource(
    profile,
    async profile => (await getWarehouses(profile.token)).map(warehouse => ({
      value: warehouse.id.toString(),
      displayValue: warehouse.name
    })),
    { initialValue: [] }
  )
  const [products] = createResource(
    profile,
    async profile => (await getProducts(profile.token)).map(product => ({
      value: product.id.toString(),
      displayValue: product.name
    })),
    { initialValue: [] }
  )
  return <div>
    <h1 style={{ "margin-bottom": "1rem" }}>库存管理</h1>
    <DataTable data={stocks()}
      head={{
        warehouse: "仓库",
        product: "商品名",
        begin: "入库时间",
        period: "保质期",
        amount: "总量",
        remaining: "余量",
        size: "体积",
        shelved: "已上架",
        expired: "已过期"
      }}
      cell={{
        warehouse: x => warehouses().find(warehouse => warehouse.value == x.toString())?.displayValue ?? "",
        product: x => products().find(product => product.value == x.toString())?.displayValue ?? "",
        begin: x => x.toLocaleDateString("zh-CN", {
          "dateStyle": "short"
        }),
        period: x => `${x} 天`,
        amount: x => x,
        remaining: x => x,
        size: x => `${x} m³`,
        shelved: x => "否是"[x],
        expired: x => "否是"[x]
      }}
      edit={{
        warehouse: (id, value) =>
          <DropdownInput name={id} id={id} required
            value={value < 0 ? undefined : value.toString()}
            displayValue={value < 0 ? undefined :
              warehouses().find(warehouse => warehouse.value == value.toString())?.displayValue
            }
            options={search => warehouses().filter(warehouse => warehouse.displayValue.includes(search))}
          />,
        product: (id, value) =>
          <DropdownInput name={id} id={id} required
            value={value < 0 ? undefined : value.toString()}
            displayValue={value < 0 ? undefined :
              products().find(product => product.value == value.toString())?.displayValue
            }
            options={search => products().filter(product => product.displayValue.includes(search))}
          />,
        begin: (id, value) =>
          <input type="datetime-local" name={id} id={id} step="any" required
            value={new Date(
              value.getTime() - value.getTimezoneOffset() * 60000
            ).toISOString().slice(0, -5)}
          />,
        period: (id, value) => <span attr:with-unit="true">
          <input type="number" name={id} id={id} value={value} min={0} step={1} required />
          天
        </span>,
        amount: (id, value) =>
          <input type="number" name={id} id={id} value={value} min={0} step={1} required />,
        remaining: (id, value) =>
          <input type="number" name={id} id={id} value={value} min={0} step={1} required />,
        size: (id, value) => <span attr:with-unit="true">
          <input type="number" name={id} id={id} value={value} min={0} step={1} required />
          m³
        </span>,
        shelved: (id, value) => <SegmentedButton type="radio" id={id} name={id} required>
          <SegmentedButtonSegment value={Bool.TRUE} checked={value == Bool.TRUE}>是</SegmentedButtonSegment>
          <SegmentedButtonSegment value={Bool.FALSE} checked={value == Bool.FALSE}>否</SegmentedButtonSegment>
        </SegmentedButton>,
        expired: (id, value) => <SegmentedButton type="radio" id={id} name={id} required>
          <SegmentedButtonSegment value={Bool.TRUE} checked={value == Bool.TRUE}>是</SegmentedButtonSegment>
          <SegmentedButtonSegment value={Bool.FALSE} checked={value == Bool.FALSE}>否</SegmentedButtonSegment>
        </SegmentedButton>,
      }}
      save={async (input, row) => {
        await updateStock(profile().token, {
          warehouse: Number(input.warehouse),
          product: Number(input.product),
          begin: new Date(input.begin),
          period: Number(input.period),
          amount: Number(input.amount),
          remaining: Number(input.remaining),
          size: Number(input.size),
          shelved: Number(input.shelved),
          expired: Number(input.expired)
        }, row?.id)
        refetch()
      }}
      default={{
        warehouse: -1,
        product: -1,
        begin: new Date(),
        period: 1,
        amount: 1,
        remaining: 1,
        size: 1,
        shelved: Bool.FALSE,
        expired: Bool.FALSE
      }} />
  </div>
}

export default Stock
