import React from "react";
import { Link } from "react-router-dom";

import { Layout, Menu } from "antd";
const { Header } = Layout;

export default () => (
  <Header>
    <div className="logo" />
    <Menu
      mode="horizontal"
      defaultSelectedKeys={["2"]}
      style={{ lineHeight: "64px" }}
    >
      <Menu.Item key="1">
        <Link to="/">Home</Link>
      </Menu.Item>
      <Menu.Item key="2">
        <Link to="/editor">Editor</Link>
      </Menu.Item>
      <Menu.Item key="3">
        <Link to="/about">About</Link>
      </Menu.Item>
    </Menu>
  </Header>
);
