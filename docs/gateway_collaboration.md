# Java 网关对接与限流协同规范

本文面向 Java 网关/后端团队，说明如何与 Python 算法服务（FastAPI）配合，实现“同一用户不频繁、多人并发不误限”的网关-算法协同策略。

---

## 1. 目标
- 用户级限流与最小间隔：同一用户短时间内高频请求将被限制（429）
- 多用户并发下的公平性：各用户互不影响，即使共享同一出口 IP
- 分层限流：不同套餐用户享受不同吞吐配额
- 可信代理：仅信任来自受信任网关的转发头，避免头部伪造

---

## 2. 网关转发必备头部
- X-User-Id: 业务唯一用户ID（必填）
- X-Client-Id: 客户端/会话ID（建议）
- X-User-Tier: 用户等级（free/pro/enterprise…）
- X-Forwarded-For / X-Real-IP: 原始客户端 IP（网关为受信任代理时有效）

注意：算法端支持通过配置调整头名（见“算法端配置”）。

---

## 3. 算法端配置（.env 或环境变量）

示例：
```
ENABLE_PROXY_HEADERS=true
TRUSTED_PROXY_IPS=["10.0.0.0/8","192.168.1.10"]
USER_ID_HEADER=x-user-id
CLIENT_ID_HEADER=x-client-id
USER_TIER_HEADER=x-user-tier
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_TIERS={"default":100,"free":60,"pro":600,"enterprise":3000}
RATE_LIMIT_DEFAULT_TIER=default
MIN_INTERVAL_PER_USER=0.5
```

说明：
- 仅当请求来源 IP 属于 TRUSTED_PROXY_IPS 中的网段/地址时，算法端才会使用 X-Forwarded-For/X-Real-IP 作为原始 IP。
- 限流键优先使用用户标识（UserId/ClientId/API Key/Authorization），不存在时才回退到 IP。

---

## 4. 建议的网关策略
- 为所有向算法服务的转发请求注入 X-User-Id（登录/匿名皆可稳定标识）。
- 对超长文本/重查询路径设置限速与熔断，降低对算法端热点打击。
- 将算法端所在主机的 IP 纳入网关回源白名单，保证路径稳定。
- 业务高峰期前，联合预热缓存与连接池。

---

## 5. 回溯与可观测性
- 建议在网关日志中打印：trace-id、user-id、client-id、user-tier、下游状态码、耗时。
- 与算法端对齐日志格式，便于跨端链路追踪；对 5xx/429 立即采样上报。

---

## 6. 最佳实践
- 匿名用户：按会话/设备指纹生成稳定 X-User-Id，避免全部回退到 IP。
- 分层：活动期间临时提升 pro/enterprise 的配额（下发 X-User-Tier），算法端自动适配。
- 防伪造：仅允许受信任网关直接访问算法端，其他来源通过 WAF/ACL 拦截。

---

## 7. 故障排查
- 若发现多人并发仍被“请求频繁”，检查：
  - 网关是否注入了 X-User-Id
  - 算法端 trusted_proxy_ips 是否包含网关对端 IP/网段
  - 是否误将所有请求当作同一匿名用户
- 若 5xx 激增：联合排查下游 LLM/向量库/DB 的连接与队列，必要时降级熔断。

