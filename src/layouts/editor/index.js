import React from "react";
import { Route } from "react-router-dom";

import Toolbar from "./components/Toolbar";

export default ({ routes }) => (
  <>
    <Toolbar />
    {routes.map((route, i) => (
      <Route
        key={i}
        exact={route.exact}
        path={route.path}
        render={props => <route.component {...props} routes={route.routes} />}
      />
    ))}
  </>
);
