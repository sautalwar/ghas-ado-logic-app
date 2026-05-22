# Limitations — Make.com Free Tier for GHAzDO → ADO

## Free Tier Constraints

### 1. Operation Limit: 1,000/month
- Each full alert cycle (create + close) uses **7-8 operations**
- Maximum **~125-142 full cycles/month** on free tier
- For teams with < 100 unique security alerts/month, this is sufficient
- **Exceeding the limit:** Scenario pauses (no data loss), events queue, email notification sent

### 2. Active Scenario Limit: 2
- Free tier allows only **2 active scenarios**
- This integration uses 1 scenario
- Leaves 1 scenario for other automations

### 3. Data Transfer: 100 MB/month
- Each alert payload is ~1-3 KB — not a concern
- 1,000 operations × 3 KB = ~3 MB (well within limit)

### 4. Execution Interval
- Webhook triggers are **instant** (not subject to 15-minute minimum interval)
- The 15-minute interval limit only applies to polling triggers

### 5. Execution History: 5 days
- Free tier retains execution logs for **5 days only**
- Paid tiers retain 30+ days
- Impact: Troubleshooting past failures beyond 5 days is not possible

---

## Functional Limitations

### 6. WIQL Not Native to ADO Module
- Make.com's Azure DevOps module does **not** support WIQL queries natively
- Dedup and work item search require the generic **HTTP module**
- This adds 1 extra operation per event and requires manual PAT/auth configuration
- **Workaround:** Already implemented via HTTP module in the scenario

### 7. No Native Tag Search
- The ADO module's "List Work Items" does not support filtering by tag
- Must use WIQL via HTTP module for tag-based lookups
- **Impact:** Slightly more complex setup; additional operation cost

### 8. PAT Management
- ADO connection uses a Personal Access Token
- PATs expire (max 1 year) — requires periodic rotation
- Make.com does not auto-rotate PATs
- **Mitigation:** Set calendar reminders; consider OAuth for longer-lived auth

### 9. Single Work Item Close per Event
- The WIQL query returns all matching work items, but the Update module only closes the **first one** (`workItems[0].id`)
- If multiple work items exist with the same tag (shouldn't happen with dedup), only the first is closed
- **Impact:** Minimal — dedup prevents this scenario

### 10. Error Handling is Basic
- Make.com free tier supports basic error handling (break, ignore, retry)
- No advanced error routing (e.g., send to dead-letter queue)
- Failed operations are logged and can trigger email notifications
- **Impact:** May need manual intervention for persistent failures

---

## What's NOT Possible on Free Tier

| Feature | Available? | Notes |
|---------|-----------|-------|
| Webhook trigger (instant) | ✅ Yes | No polling delay |
| Create work item | ✅ Yes | Via ADO module |
| Update/close work item | ✅ Yes | Via ADO module |
| WIQL dedup query | ✅ Yes | Via HTTP module (workaround) |
| Custom error webhooks | ❌ No | Paid feature |
| Data store (persistent) | ⚠️ Limited | 1 data store, 1 MB on free tier |
| Team collaboration | ❌ No | Free tier is single-user |
| Execution history > 5 days | ❌ No | 5-day retention on free tier |
| Parallel executions | ❌ No | Sequential only on free tier |
| API access to scenarios | ❌ No | Paid feature |
| Custom variables via API | ❌ No | Must configure in UI |

---

## Comparison: Make.com Free vs Paid

| Feature | Free | Core ($9/mo) | Pro ($16/mo) |
|---------|------|-------------|-------------|
| Operations/month | 1,000 | 10,000 | 10,000 |
| Active scenarios | 2 | Unlimited | Unlimited |
| Execution interval | 15 min* | 5 min* | 1 min* |
| Data transfer | 100 MB | 1 GB | 1 GB |
| Execution history | 5 days | 30 days | 60 days |
| Data stores | 1 (1 MB) | Unlimited | Unlimited |
| Team members | 1 | 1 | Unlimited |
| Priority execution | No | No | Yes |

*Applies only to polling triggers; webhooks are always instant

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Exceed 1,000 ops/month | Medium | Scenario pauses | Monitor usage; upgrade if needed |
| PAT expires | Certain (eventually) | Scenario fails silently | Calendar reminder; OAuth alternative |
| Make.com outage | Low | Events queue (no data loss) | ADO Service Hook retries; manual fallback |
| Payload format changes | Very Low | JSON parse fails | Update data structure in Make.com |
| Free tier discontinued | Very Low | Must upgrade or migrate | $9/mo Core tier is affordable fallback |

---

## When to Upgrade from Free Tier

Consider upgrading to Make.com Core ($9/month) if:
- Alert volume exceeds ~100 unique alerts/month consistently
- You need execution history beyond 5 days for auditing
- You want to add additional automations (> 2 scenarios)
- Team collaboration is needed (multiple users managing scenarios)

Consider upgrading to Logic App ($50-100/month) if:
- Alert volume is high (> 500 alerts/month)
- You need enterprise-grade reliability (SLA-backed)
- Managed Identity is required (no PAT management)
- You need deep Azure Monitor integration
- One-click deployment via "Deploy to Azure" button is preferred
