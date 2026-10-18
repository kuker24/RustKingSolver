---
name: scopesentry
description: "ScopeSentry MCP operator playbook: projects, scan tasks/templates, assets (domain/subdomain/IP/URL/vuln), nodes. Trigger: ScopeSentry, scopesentry MCP, ssk_ API key, list_assets, create_scan_task, asset sync."
---

# ScopeSentry MCP

Requires a **live ScopeSentry** instance. omp MCP stub (disabled until keyed):

```json
// ~/.omp/agent/mcp.json → mcpServers.scopesentry
{
  "type": "http",
  "url": "http://<host>:8082/mcp",
  "headers": { "X-API-Key": "ssk_…" },
  "enabled": false
}
```

Enable after filling URL + key, then `/mcp reload`.

## Tools (MCP)

| Tool | Use |
|---|---|
| `list_projects` / `list_projects_data` / `get_project` / `create_project` | project tree |
| `list_tasks` / `get_task` / `create_scan_task` | scan jobs |
| `list_scan_templates` / `get_scan_template` / `create_scan_template` | templates |
| `list_plugin_modules` / `list_plugins` | pipeline plugins |
| `list_assets` / `count_assets` / `get_asset_detail` / `add_asset_tag` | asset query |
| `list_nodes` | scan nodes |

## Workflows

### Assets by project

1. `list_projects` → ObjectID  
2. `list_assets` with `filter.project: ["<ObjectID>"]` (ID only, never Chinese name)

### Two-phase root-domain collect

1. `targetSource: general` + SubdomainScan(+Security) template  
2. Wait `get_task` done  
3. `targetSource: subdomain` + `search: task=="<phase1 name>"` for ports/vulns

Distributed tasks shard per **target**; scanning a root domain on one node keeps its children there — split phases for parallelism.

### search DSL (not SQL)

| Op | Meaning | Index |
|---|---|---|
| `==` | exact | yes |
| `=^prefix` / value starting `^` | prefix | yes |
| `=` | regex fuzzy | **no** |
| `&&` / `\|\|` / `!=` | boolean | — |

`project` belongs in `filter`, never in `search`. Prefer `==` / `^` on indexed fields (`domain`, `ip`, `port`, `title`, …).

### filter

Same-key values = OR; different keys = AND. Common keys: `project`, `task` (task **name**), `port`, `service`, `app`, `level`, `tags`.

## omp wiring

```
ROUTE: skill://hypeking/scopesentry/SKILL.md
MCP:   scopesentry (http) — enable when instance ready
NEXT:  list_projects → list_assets / create_scan_task
```

Provenance: [Hinln/ARTEX](https://github.com/Hinln/ARTEX) `skills/scopesentry` (AGPL-3.0). Full upstream body retained below for tool-field detail.

---

# Upstream playbook (ARTEX)

面向**已部署 ScopeSentry 实例**的用户。通过 MCP 客户端连接平台，无需本地源码。

## 1. 准备工作

### 1.1 确认服务可访问

- 默认 Web 界面：`http://<主机>`
- MCP 端点：`http://<主机>/mcp`（若前面有反向代理或前端代理，以实际 `/mcp` 地址为准）

### 1.2 创建 API Key

1. 浏览器登录 ScopeSentry Web 界面
2. 进入 **API Key** 管理页创建密钥
3. 保存返回的 `ssk_...` 字符串（**仅显示一次**）

也可使用：`Authorization: Bearer ssk_你的密钥`

## 2. 常用工作流细节

### 2.1 按项目查资产

当用户或上下文**已有项目条件**时，优先带上 `filter.project` 缩小范围。

```json
{
  "asset_type": "asset",
  "pageIndex": 1,
  "pageSize": 20,
  "search": "domain=^example.com",
  "filter": {
    "project": ["<项目ObjectID>"]
  }
}
```

### 2.2 创建扫描任务

1. `list_nodes` 获取在线节点名称
2. `list_scan_templates` 或 `create_scan_template` 获取模板 **ObjectID**
3. `create_scan_task`：`name`、`node` 必填，`template` 填模板 ID

**targetSource：**

| targetSource | 说明 | 必填 |
| --- | --- | --- |
| `general` | 直接输入目标 | `target` |
| `project` | 从项目读取 | `project` |
| `asset` / `RootDomain` / `subdomain` / `UrlScan` | 从资产库搜索 | `search` (+ optional project/filter) |

**示例 — 直接扫根域名：**

```json
{
  "name": "example-子域名收集",
  "node": ["node-1"],
  "template": "<模板ObjectID>",
  "targetSource": "general",
  "target": "example.com\nfoo.com",
  "project": ["<项目ObjectID>"]
}
```

**示例 — 从子域名库续扫：**

```json
{
  "name": "example-端口与漏洞",
  "node": ["node-1"],
  "template": "<后续模块模板ObjectID>",
  "targetSource": "subdomain",
  "search": "task==\"example-子域名收集\"",
  "project": ["<项目ObjectID>"]
}
```

### 2.3 asset_type

`asset`, `RootDomain`, `subdomain`, `app`, `mp`, `UrlScan`, `SensitiveResult`, `DirScanResult`, `crawler`, `vulnerability`, `PageMonitoring`, `IPAsset`, `SubdomainTakerResult`

Aliases: `web`→asset, `vuln`→vulnerability, `ip`→IPAsset, `url`→UrlScan

Need totals → `count_assets` (same filters as `list_assets`), do not page just to count.

## 3. Complements

| Need | Pack |
|---|---|
| Local web pipeline | `HackinMode` / axiom-web-pwn |
| Frontend API harvest | `pwn-api-recon` |
| Classic recon agents | `pwn-recon` |
