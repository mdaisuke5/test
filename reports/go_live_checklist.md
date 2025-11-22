# Go-Live Checklist

- [ ] API credentials configured in `.env` and validated via test order on demo.
- [ ] Redis, Prometheus, Grafana containers healthy; dashboards populated.
- [ ] Clock sync (NTP) confirmed on host and containers.
- [ ] Backfill recent session data into `./data/min_bar/` and `./data/tick/`.
- [ ] Dry-run paper session passes risk gates: Sharpe ≥ 1.2, intraday DD < 2%.
- [ ] Slack webhook responds to test alert; Loki receiving structlog JSON.
- [ ] kabuステーション® maintenance token refresh verified at 06:15 JST.
- [ ] Trade throttle parameters match risk policy (≤6/hour, ≤20/day).
- [ ] Overnight flat rule applied when night session disabled.
- [ ] Deployment tag pushed; Docker image built by CI and scanned for vulnerabilities.
