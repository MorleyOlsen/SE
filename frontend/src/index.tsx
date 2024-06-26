/* @refresh reload */
import { Route, HashRouter as Router } from "@solidjs/router"
import { render } from "solid-js/web"
import "./index.css"
import Index from "./routes"
import DashboardIndex from "./routes/dashboard"
import Breed from "./routes/dashboard/breed"
import Farm from "./routes/dashboard/farm"
import DashboardLayout from "./routes/dashboard/layout"
import { Market, MarketItem } from "./routes/dashboard/market"
import Order from "./routes/dashboard/order"
import Production from "./routes/dashboard/production"
import Profile from "./routes/dashboard/profile"
import Sales from "./routes/dashboard/sales"
import Stock from "./routes/dashboard/stock"
import Warehouse from "./routes/dashboard/warehouse"

const root = document.getElementById("app")

render(() => <Router>
  <Route path="/" component={Index} />
  <Route path="/dashboard" component={DashboardLayout}>
    <Route path="/" component={DashboardIndex} />
    <Route path="/profile" component={Profile} />
    <Route path="/farm" component={Farm} />
    <Route path="/breed" component={Breed} />
    <Route path="/production" component={Production} />
    <Route path="/warehouse" component={Warehouse} />
    <Route path="/stock" component={Stock} />
    <Route path="/sales" component={Sales} />
    <Route path="/order" component={Order} />
    <Route path="/market" component={Market} />
    <Route path="/market/:id" component={MarketItem} />
  </Route>
</Router>, root!)
