import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { Layout } from "antd";
import "./App.css";

import HomeLayout from "./layouts/home";
import EditorLayout from "./layouts/editor";

import Editor from "./views/Editor";
import About from "./views/About";
import Home from "./views/Home";

const routes = [
  {
    path: "/",
    component: HomeLayout,
    routes: [
      {
        path: "/about",
        component: About
      },
      {
        path: "/",
        exact: true,
        component: Home
      }
    ]
  },
  {
    path: "/editor",
    component: EditorLayout,
    routes: [
      {
        path: "/",
        component: Editor
      }
    ]
  }
];

export default () => (
  <Router>
    <Layout className="layout">
      <Switch>
        {routes.map((route, i) => (
          <Route
            key={i}
            exact
            path={route.path}
            render={props => (
              <route.component {...props} routes={route.routes} />
            )}
          />
        ))}
      </Switch>
    </Layout>
  </Router>
);
