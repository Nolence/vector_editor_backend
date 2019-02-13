import React from "react";
import { Route } from "react-router-dom";

import Toolbar from "./components/Toolbar";

export default ({ routes }) => {
  return (
    <>
      <Toolbar />
      {routes.map((route, i) => (
        <Route
          key={i}
          path={route.path}
          exact={route.exact}
          render={props => (
            // pass the sub-routes down to keep nesting
            <route.component {...props} routes={route.routes} />
          )}
        />
      ))}
    </>
  );
};
