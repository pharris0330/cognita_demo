# Quick Reference: Pain Point → Command

> All commands run on a single line in Git Bash. Server must be running on port 8001.

---

## 🚀 Start the Server

```bash
cd ~/PaulStuff/github-mcp-server-v2 && REPO_PATH=./sample-repo python -m uvicorn src.api_v2:app --port 8001
```

---

## Pain Point #1: "My 42MB codebase doesn't fit in AI context"

**Solution:** Smart context selection finds only relevant files.

```bash
curl -s -X POST http://localhost:8001/context -H "Content-Type: application/json" -d "{\"task\": \"Add retry logic to DynamoDB handler\", \"max_tokens\": 30000, \"include_docs\": true}" | python -m json.tool
```

**What you get:** Top 10-20 relevant files with relevance scores, auto-includes runbooks.

---

## Pain Point #2: "I copy-paste between Claude, GPT, and Bedrock constantly"

**Solution:** One command runs all 3 AIs with identical context.

```bash
curl -s -X POST http://localhost:8001/orchestrate -H "Content-Type: application/json" -d "{\"task\": \"Add exponential backoff retry logic to the stream handler\", \"include_docs\": true}" --max-time 180 | python -m json.tool
```

**What you get:** Claude writes code, GPT reviews for bugs, Bedrock checks AWS best practices. ~60-90 seconds, ~$0.08.

---

## Pain Point #3: "AI code deploys, then fails with AccessDeniedException"

**Solution:** IAM-aware orchestration flags missing permissions before deploy.

```bash
curl -s -X POST http://localhost:8001/orchestrate -H "Content-Type: application/json" -d "{\"task\": \"Add SNS notification when order is created\", \"include_docs\": true}" --max-time 180 | python -m json.tool
```

**Look for in response:**
```json
"iam_analysis": {
  "missing_permissions": ["sns:Publish"],
  "terraform_update": "..."
}
```

**What you get:** PR includes both code AND Terraform IAM updates. One merge, no AccessDenied.

---

## Pain Point #4: "When AI code breaks production, debugging takes hours"

**Solution:** Paste error, get root cause + fix in 60 seconds.

### Diagnose Only
```bash
curl -s -X POST http://localhost:8001/diagnose -H "Content-Type: application/json" -d "{\"error_message\": \"ProvisionedThroughputExceededException: Rate exceeded\", \"file_path\": \"src/handlers/stream_handler.py\", \"related_pr\": 6}" --max-time 180 | python -m json.tool
```

### Diagnose AND Create Fix PR
```bash
curl -s -X POST http://localhost:8001/diagnose-and-fix -H "Content-Type: application/json" -d "{\"error_message\": \"TimeoutError: Lambda timed out after 30 seconds\", \"file_path\": \"src/handlers/batch_processor.py\"}" --max-time 180 | python -m json.tool
```

**What you get:** Root cause, confidence level (high/medium/low), and a ready-to-merge fix PR.

---

## Pain Point #5: "If a PR causes chaos, I can't undo it fast enough"

**Solution:** Every AI PR tracked. One-click rollback.

### List All AI PRs
```bash
curl -s http://localhost:8001/prs/ai | python -m json.tool
```

### Check If PR Can Be Rolled Back
```bash
curl -s http://localhost:8001/pr/6/status | python -m json.tool
```

### Execute Rollback
```bash
curl -s -X POST http://localhost:8001/rollback -H "Content-Type: application/json" -d "{\"pr_number\": 6, \"reason\": \"Causing production throttling errors\"}" | python -m json.tool
```

**What you get:** Revert PR created automatically. You approve, code goes back to safe state.

---

## 💰 Cost Tracking

### View Session Costs
```bash
curl -s http://localhost:8001/costs | python -m json.tool
```

### Estimate Before Running
```bash
curl -s "http://localhost:8001/costs/estimate?provider=claude&input_tokens=30000&output_tokens=2000" | python -m json.tool
```

---

## 🔧 Workflow Automation

### Create Branch + Commit + PR (One Command)
```bash
curl -s -X POST http://localhost:8001/workflow -H "Content-Type: application/json" -d "{\"task\": \"Add retry logic to stream handler\", \"files\": {\"src/utils/retry.py\": \"# Your code here\"}}" | python -m json.tool
```

---

## ✅ Health Check

```bash
curl -s http://localhost:8001/health | python -m json.tool
```

---

## 📋 Endpoint Summary

| Pain Point | Endpoint | Method |
|------------|----------|--------|
| Context too big | `/context` | POST |
| Tool sprawl | `/orchestrate` | POST |
| IAM issues | `/orchestrate` | POST (check `iam_analysis`) |
| Production errors | `/diagnose` | POST |
| Error → Fix PR | `/diagnose-and-fix` | POST |
| List AI PRs | `/prs/ai` | GET |
| Check rollback | `/pr/{id}/status` | GET |
| Execute rollback | `/rollback` | POST |
| View costs | `/costs` | GET |
| Create PR | `/workflow` | POST |

---

## 🎯 Typical Workflow

```bash
# 1. Find relevant context
curl -s -X POST http://localhost:8001/context -H "Content-Type: application/json" -d "{\"task\": \"YOUR TASK HERE\"}" | python -m json.tool

# 2. Run 3-AI orchestration
curl -s -X POST http://localhost:8001/orchestrate -H "Content-Type: application/json" -d "{\"task\": \"YOUR TASK HERE\"}" --max-time 180 | python -m json.tool

# 3. Create PR with the code
curl -s -X POST http://localhost:8001/workflow -H "Content-Type: application/json" -d "{\"task\": \"YOUR TASK HERE\", \"files\": {\"filename.py\": \"# code\"}}" | python -m json.tool

# 4. Check costs
curl -s http://localhost:8001/costs | python -m json.tool
```

---

## ⚠️ Tips

- All commands must be on **a single line** in Git Bash
- Long-running commands use `--max-time 180` to prevent timeout
- Pipe to `| python -m json.tool` for readable JSON output
- Confidence levels: **high** = GPT approved, **low** = GPT found issues
- Average cost: **~$0.08** per 3-AI orchestration

---

*Questions? Run `/health` first to verify the server is up.*
