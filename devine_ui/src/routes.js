import Index from "views/Index.js";
import PowerDispatch from "views/examples/PowerDispatch.js";
import Maps from "views/examples/Maps.js";
import Register from "views/examples/Register.js";
import Login from "views/examples/Login.js";
import Notifications from "views/examples/Notifications.js";
import Icons from "views/examples/Icons.js";

var routes = [
  {
    path: "/index",
    name: "Dashboard",
    icon: "ni ni-tv-2 text-primary",
    component: Index,
    layout: "/admin"
  },
  // {
  //   path: "/icons",
  //   name: "Power Dispatch",
  //   icon: "ni ni-planet text-blue",
  //   component: Icons,
  //   layout: "/admin"
  // },
  // {
  //   path: "/maps",
  //   name: "Maps",
  //   icon: "ni ni-pin-3 text-orange",
  //   component: Maps,
  //   layout: "/admin"
  // },
  {
    path: "/user-profile",
    name: "Power Dispatch",
    icon: "ni ni-single-02 text-yellow",
    component: PowerDispatch,
    layout: "/admin"
  },
  {
    path: "/tables",
    name: "Alerts & Notifications",
    icon: "ni ni-bullet-list-67 text-red",
    component: Notifications,
    layout: "/admin"
  },
];
export default routes;
