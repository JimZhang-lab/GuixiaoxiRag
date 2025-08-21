```
python tests/comprehensive_stress_test.py --url http://localhost:8002 --users 3000 --duration 1800 --ramp-up 900 --pool-size 20000 --per-host 6000 --timeout 60 --buffer-size 2000000 --metrics-interval 5 --progress-interval 30 --gc-interval 500 --min-interval-per-user 0.5 --spoof-client-ip --quiet
```

# 压测命令合集

## 基础环境
```bash
conda activate lightrag312
export API_BASE=http://localhost:8002
```

## 快速验证
- 单用户高频（预期触发限流，需在 .env 设置较小 RATE_LIMIT_REQUESTS 或 MIN_INTERVAL_PER_USER>0）：
```bash
python tests/comprehensive_stress_test.py --url $API_BASE --users 1 --duration 30 --ramp-up 1 --pool-size 200 --per-host 100 --timeout 60 --buffer-size 5000 --metrics-interval 3 --progress-interval 10 --gc-interval 50 --min-interval-per-user 0 --user-tier free --quiet
```
- 多用户并发（不误限，需要 --spoof-client-ip 或网关注入用户头）：
```bash
python tests/comprehensive_stress_test.py --url $API_BASE --users 500 --duration 60 --ramp-up 10 --pool-size 5000 --per-host 2000 --timeout 60 --buffer-size 200000 --metrics-interval 3 --progress-interval 10 --gc-interval 200 --min-interval-per-user 0.2 --user-tier free --spoof-client-ip --quiet
```

## 典型场景
- 1000 用户，10 分钟：
```bash
python tests/comprehensive_stress_test.py --url $API_BASE --users 1000 --duration 600 --ramp-up 300 --pool-size 10000 --per-host 4000 --timeout 60 --buffer-size 800000 --metrics-interval 5 --progress-interval 20 --gc-interval 300 --min-interval-per-user 0.3 --user-tier pro --spoof-client-ip --quiet
```
- 3000 用户，30 分钟：
```bash
python tests/comprehensive_stress_test.py --url $API_BASE --users 3000 --duration 1800 --ramp-up 900 --pool-size 20000 --per-host 6000 --timeout 60 --buffer-size 2000000 --metrics-interval 5 --progress-interval 30 --gc-interval 500 --min-interval-per-user 0.5 --spoof-client-ip --user-tier pro --quiet
```

## 观测与报告
- 压测结束后在 tests/ 目录生成：
  - stress_test_report_*users_*.json 与 *_summary.json
- 关注指标：成功率、RPS、P95/P99、各 endpoint 失败分布、error_samples 采样

## 小贴士
- 若通过 Java 网关转发，请在网关注入：X-User-Id / X-Client-Id / X-User-Tier；并将网关对端 IP/CIDR 配置到 trusted_proxy_ips
- 算法端默认 LLM/Embedding/Rerank 超时均为 240s，可通过 .env 调整；长链路（hybrid/mix/global）建议提升服务端/上游超时
- 对单用户热点路径可适当升高最小间隔；对超长文本/复杂模式建议做限速与降级
