# Limitations — Zapier Integration

> Known constraints, trade-offs, and mitigation strategies

---

## 1. Free Tier Is Not Sufficient

| Limitation | Impact |
|-----------|--------|
| Free tier: 5 Zaps, 100 tasks/month, single-step only | Cannot build this integration on free tier |
| Multi-step Zaps require Starter ($20/mo) or higher | Minimum cost: $20/month |
| Webhooks by Zapier trigger is Starter+ | Free tier cannot receive webhooks |

**Mitigation:** Start with free tier for testing, upgrade to Starter before production. Professional ($49/mo) if volume exceeds 750 tasks/month.

---

## 2. Native Zapier Consumer Does NOT Support GHAzDO Events

| Limitation | Impact |
|-----------|--------|
| ADO's built-in Zapier consumer only supports standard events | Cannot use direct ADO↔Zapier path for GHAzDO alerts |
| GHAzDO events (`advancedsecurity.alert.*`) are not in native consumer list | Must use Web Hooks consumer as intermediary |

**Detail:** The ADO Service Hooks Zapier consumer supports: work item events, code push, build complete, release events, and TFVC checkin. It does **not** include the newer `advancedsecurity.alert.created` or `advancedsecurity.alert.stateChanged` events.

**Mitigation:** Use the **Web Hooks** consumer in ADO Service Hooks, pointing to Zapier's Catch Hook URL. Functionally identical — just requires the intermediary webhook step.

---

## 3. Deduplication Is Partial

| Limitation | Impact |
|-----------|--------|
| Dedup relies on WIQL search by tag | Extra API call per alert (costs a Zapier task) |
| Race condition possible | If two hooks fire simultaneously, both may pass the dedup check |
| Tag must match exactly | Any mismatch in tag format between create and search breaks dedup |

**Mitigation:**
- Race conditions are rare (ADO Service Hooks have natural ordering)
- Test tag format consistency between Zap #1 (create) and Zap #2 (close)
- Consider adding a small delay (Zapier's "Delay" action) if race conditions occur

---

## 4. Task Consumption Adds Up

| Scenario | Tasks per event | Monthly capacity (Starter) |
|----------|----------------|--------------------------|
| Alert created (new) | 5 tasks | 150 creates/month |
| Alert created (duplicate) | 4 tasks | 187 dedup checks/month |
| Alert state changed | 4-5 tasks | 150-187 closes/month |
| Full lifecycle (create + close) | ~9-10 tasks | ~75 full cycles/month |

**Mitigation:**
- Use Filters early — stopped filters don't count as tasks
- Scope Service Hooks to specific repos (reduce noise)
- Consider Professional tier ($49/mo) for 2,000 tasks/month
- Use Paths (Professional) to combine both Zaps → saves 1 task per event

---

## 5. No Git-Based Version Control

| Limitation | Impact |
|-----------|--------|
| Zap configurations live in Zapier's cloud | Cannot version control in Git |
| No export/import for Zap definitions | Manual recreation if account is lost |
| No code review for workflow changes | Changes not auditable via PR process |

**Mitigation:**
- Document all Zap configurations in this repo (as done here)
- Take screenshots of each Zap step for reference
- Zapier has a "Zap History" feature for basic audit trail

---

## 6. PAT-Based Authentication

| Limitation | Impact |
|-----------|--------|
| ADO PAT stored in Zapier Zap steps | Must be rotated manually when expired |
| No Managed Identity support | Cannot use Azure AD for auth (unlike Logic Apps) |
| PAT scope must include Work Items R/W | Security: broad scope needed |

**Mitigation:**
- Create a dedicated service account PAT with minimal scope
- Set PAT expiration reminders (max 1 year in ADO)
- Use Zapier's built-in secret storage (stored encrypted)
- When PAT expires, update both Zaps manually

---

## 7. No Built-in Retry/Error Recovery

| Limitation | Impact |
|-----------|--------|
| Zapier retries failed tasks but with limits | Professional has Autoreplay; Starter does not |
| No exponential backoff built-in | ADO rate limits could cause cascading failures |
| Failed tasks require manual replay on Starter | Missed alerts if not monitored |

**Mitigation:**
- Monitor Zapier Task History regularly
- Set up Zapier email notifications for failures
- Professional tier includes Autoreplay (auto-retry failed tasks)
- ADO rate limits are generous for typical alert volumes

---

## 8. Single Tenant / Single Project

| Limitation | Impact |
|-----------|--------|
| Each Zap is configured for one ADO org/project | Multi-project requires duplicate Zaps |
| Service Hooks are per-project | Must configure hooks in each project |
| PAT is scoped to one organization | Multi-org requires separate PATs |

**Mitigation:**
- For multi-project: duplicate Zaps with different URLs
- Consider Logic App approach for enterprise multi-project scenarios
- Use Zapier's folder organization to group related Zaps

---

## 9. Latency

| Limitation | Impact |
|-----------|--------|
| Zapier polling interval: ~1-2 min (for non-instant triggers) | Catch Hook is instant — no polling delay |
| End-to-end: 15-60 seconds typically | Acceptable for security alert workflows |
| ADO Service Hook delivery: < 5 seconds | Minimal delay from ADO side |

**Note:** Catch Hook (webhook) triggers are **instant** — Zapier processes them immediately. The 1-2 minute polling delay only applies to scheduled/polling triggers (not used here).

---

## 10. Zapier Platform Dependency

| Limitation | Impact |
|-----------|--------|
| Zapier is a third-party SaaS | Dependency on Zapier's availability |
| Pricing can change | Future cost increases possible |
| Feature changes | Zapier may deprecate or change APIs |
| Data flows through Zapier's servers | Webhook payloads transit through Zapier |

**Mitigation:**
- Zapier has 99.9% uptime SLA
- SOC 2 Type II certified
- Data encrypted in transit and at rest
- Consider Logic App if data residency is a hard requirement

---

## Comparison: What Zapier Can vs. Cannot Do

| Capability | Status | Notes |
|-----------|--------|-------|
| Receive GHAzDO alerts | ✅ Yes | Via Web Hooks consumer → Catch Hook |
| Parse webhook payload | ✅ Yes | Code by Zapier (JavaScript) |
| Create ADO work item | ✅ Yes | Via ADO REST API |
| Handle all 3 alert types | ✅ Yes | Code step handles all types |
| Auto-close on resolved | ✅ Yes | Zap #2 with WIQL search + PATCH |
| Deduplicate | ⚠️ Partial | WIQL search step — possible race condition |
| Managed Identity auth | ❌ No | PAT-based only |
| Git version control | ❌ No | Zap configs in Zapier cloud |
| One-click deploy | ❌ No | Manual setup required |
| Multi-project | ⚠️ Manual | Requires duplicating Zaps per project |
| Error recovery | ⚠️ Tier-dependent | Autoreplay on Professional only |

---

## When to Choose Zapier vs. Alternatives

| Choose Zapier if... | Choose something else if... |
|---------------------|----------------------------|
| Team is familiar with Zapier | Team prefers Azure-native tools → Logic App |
| No Azure infrastructure desired | Zero cost required → Make.com free tier or Teams Notifications |
| Alert volume is moderate (<200/month) | High volume (>500/month) → Logic App or Azure Functions |
| Quick setup is priority | One-click deploy needed → Logic App with deploy button |
| Non-technical team manages it | Full audit trail needed → Logic App with Azure Monitor |
