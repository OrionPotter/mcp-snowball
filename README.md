# 雪球MCP项目

## 项目简介

雪球MCP项目旨在提供一个高效的API服务，用于获取雪球平台的股票数据。项目使用Python语言开发，基于httpx库进行异步HTTP请求。

## 功能

- 获取股票实时行情数据
- 获取股票现金流数据
- 获取股票财务指标数据

## 安装步骤

1. 克隆项目代码到本地：
   ```bash
   git clone <仓库地址>
   ```

2. 进入项目目录：
   ```bash
   cd snowball
   ```

3. 安装项目依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 启动MCP服务：
   ```bash
   python xueqiu_mcp_server.py
   ```

2. 使用提供的API工具获取股票数据。

## 依赖项

- Python >= 3.13
- httpx >= 0.28.1
- mcp[cli] >= 1.6.0

## 贡献

欢迎提交问题和请求合并。请确保在提交前运行所有测试用例。