# GitHub MCP Server - Demo #4

**AI Orchestration Layer for Multi-AI Collaboration on Large Codebases**

Demo #4 enables multiple AI tools (Claude, GPT-4, Amazon Bedrock) to work together on enterprise codebases with consistent context, semantic search, cost tracking, and GitHub workflow automation.

## The Problem

Enterprise teams face "AI tool sprawl" when working with large codebases:

- **42MB+ codebases** hit token limits (128K-200K) when copying to AI tools
- **Multiple AI tools** (Claude, GPT, Amazon Q) lose context consistency
- **Manual file transfers** between tools waste time and introduce errors
- **No cost visibility** across AI providers
- **AI suggestions** require manual implementation into code

## The Solution

This MCP Server creates an orchestration layer that:

1. **RAG Pipeline** - Embeddings, chunking, and semantic search over your codebase
2. **Smart Context Selection** - Selects the right 1-2% of your codebase (30K tokens from millions)
3. **Multi-AI Pipeline** - Claude implements, GPT reviews, Bedrock optimizes AWS
4. **Cost Tracking** - Per-call costs with session totals by provider
5. **GitHub Automation** - AI suggestions become PRs automatically

---

## Demo #4 Features

### 1. Full RAG Pipeline (Embeddings + Semantic Search)

Complete vector search implementation for intelligent context retrieval.

**Components:**

| Component | Description |
|-----------|-------------|
| **Chunking** | 1000-char chunks with 200-char overlap |
| **Embeddings** | OpenAI `text-embedding-3-small` or local `all-MiniLM-L6-v2` |
| **Vector Store** | ChromaDB for fast similarity search |
| **Semantic Search** | Cosine similarity with filtering by file type |

**Embedding Providers:**

| Provider | Model | Dimensions | Use Case |
|----------|-------|------------|----------|
| OpenAI | text-embedding-3-small | 1536 | Production (best quality) |
| Local | all-MiniLM-L6-v2 | 384 | Offline / cost-sensitive |
| Mock | Hash-based | 384 | Testing without API calls |

```python
from src.vectorstore import VectorStore

# Initialize and index
vs = VectorStore("./my-repo", embedding_provider="openai")
vs.index_repository()

# Semantic search
results = vs.search("authentication retry logic", limit=5)
for r in results:
    print(f"{r.path}: {r.score:.3f}")

# Filtered search
code_only = vs.search_code("handler function")
docs_only = vs.search_docs("API reference")
```

### 2. Enhanced Context Gathering

Automatically discovers and includes documentation alongside code.

- **Auto-discovery**: README, runbooks, API docs, architecture docs
- **Token budget split**: 70% code, 30% documentation (configurable)
- **Relevance scoring**: Combines semantic similarity with keyword matching
- **Supported formats**: `.md`, `.rst`, `.txt`, `.adoc`

```bash
POST /context
{
  "task": "Add retry logic to DynamoDB handler",
  "max_tokens": 30000,
  "include_docs": true
}
```

### 3. Multi-AI Orchestration with Cost Tracking

Run a 3-AI pipeline with full cost visibility.

| Step | Provider | Task |
|------|----------|------|
| 1 | Claude (Anthropic) | Implementation |
| 2 | GPT-4o (OpenAI) | Code Review |
| 3 | Bedrock (AWS) | AWS Optimization |

```bash
POST /orchestrate
{
  "task": "Add exponential backoff to stream handler",
  "include_docs": true
}
```

**Response includes:**
```json
{
  "ai_responses": [...],
  "synthesis": "Combined AI insights...",
  "costs": {
    "this_request_usd": 0.055,
    "session_total_usd": 0.055,
    "by_provider": {
      "claude-sonnet": {"calls": 1, "cost_usd": 0.031},
      "gpt4o": {"calls": 1, "cost_usd": 0.013},
      "bedrock-claude": {"calls": 1, "cost_usd": 0.011}
    }
  }
}
```

### 4. GitHub Workflow Automation

Complete branch -> commit -> PR in one API call.

```bash
POST /workflow
{
  "task": "Add retry logic to DynamoDB handler",
  "files": {
    "src/handlers/stream_handler.py": "# AI-generated code..."
  },
  "ai_provider": "claude",
  "base_branch": "main"
}
```

**Result:**
```json
{
  "success": true,
  "branch": {
    "name": "ai/claude/add-retry-logic-20251201-1502",
    "created": true
  },
  "commits": [
    {"path": "src/handlers/stream_handler.py", "action": "created"}
  ],
  "pull_request": {
    "number": 2,
    "url": "https://github.com/owner/repo/pull/2",
    "title": "[AI] Add retry logic to DynamoDB handler"
  }
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub MCP Server                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                   RAG Pipeline                          │     │
│  │                                                         │     │
│  │   Files --> Chunking --> Embeddings --> ChromaDB       │     │
│  │              (1000 char)   (OpenAI/     (Vector         │     │
│  │                            Local)        Storage)       │     │
│  │                                              |          │     │
│  │                                              v          │     │
│  │                                      Semantic Search    │     │
│  └────────────────────────────────────────────────────────┘     │
│                              |                                   │
│                              v                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Context    │  │    Multi-AI  │  │   GitHub     │          │
│  │   Manager    │  │ Orchestrator │  │   Workflow   │          │
│  │              │  │              │  │              │          │
│  │ - Code files │  │ - Claude     │  │ - Branches   │          │
│  │ - Doc files  │  │ - GPT-4o     │  │ - Commits    │          │
│  │ - Relevance  │  │ - Bedrock    │  │ - PRs        │          │
│  │ - 70/30 split│  │ - Costs      │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                   Cost Tracker                        │       │
│  │   - Per-call tracking    - Session totals            │       │
│  │   - By provider          - By task type              │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          v                    v                    v
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ Anthropic│        │  OpenAI  │        │   AWS    │
    │  Claude  │        │  GPT-4o  │        │ Bedrock  │
    └──────────┘        └──────────┘        └──────────┘
```

---

## Installation

### Prerequisites

- Python 3.10+
- API keys for Claude, GPT-4, and AWS Bedrock
- GitHub Personal Access Token (with repo permissions)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/github-mcp-server-v2.git
cd github-mcp-server-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

**Core:**
- `fastapi`, `uvicorn` - API server
- `anthropic`, `openai`, `boto3` - AI providers
- `PyGithub` - GitHub automation

**RAG Pipeline:**
- `chromadb` - Vector database
- `sentence-transformers` - Local embeddings (optional)
- `torch` - For sentence-transformers

### Configuration

Create a `.env` file:

```properties
# AI Provider Keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...

# AWS (for Bedrock) - uses AWS credential chain
AWS_REGION=us-east-1

# GitHub
GITHUB_TOKEN=github_pat_...
GITHUB_REPO=owner/repo-name

# Optional
USE_MOCK_AI=false  # Set true for testing without API calls
```

### GitHub Token Permissions

Create a fine-grained token at https://github.com/settings/tokens?type=beta with:

- **Repository access**: Select your target repo
- **Permissions**:
  - Contents: Read and Write
  - Pull requests: Read and Write
  - Metadata: Read-only

---

## Usage

### Start the Server

```bash
REPO_PATH=./your-codebase python -m uvicorn src.api_v2:app --port 8001
```

### Run the Demos

```bash
# Quick test (8 endpoints)
python demo4/test_quick.py

# Full demo (all features)
python demo4/demo_full.py

# Vector store / RAG demo
python demo4/demo_vectorstore.py

# Skip GitHub workflow
python demo4/demo_full.py --skip-workflow
```

### API Endpoints

#### Vector Store / RAG

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/index` | POST | Index repository into vector store |
| `/search/semantic` | POST | Semantic search with embeddings |
| `/vectorstore/stats` | GET | Vector store statistics |

#### Context

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/context` | POST | Get relevant code + docs for a task |
| `/search` | GET | Search files by pattern |
| `/docs/search` | POST | Search documentation |

#### Orchestration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/orchestrate` | POST | Run 3-AI pipeline |
| `/orchestrate/consensus` | POST | All AIs on same task |

#### GitHub Workflow

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/workflow` | POST | Complete branch -> commit -> PR |
| `/branch` | POST | Create feature branch |
| `/commit` | POST | Commit file to branch |
| `/pr` | POST | Create pull request |

#### Cost Tracking

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/costs` | GET | Session cost summary |
| `/costs/estimate` | GET | Estimate before running |
| `/costs/reset` | POST | Reset session tracking |

#### Info

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System status |
| `/tools` | GET | List all endpoints |

---

## Example: Complete Workflow

```python
import httpx

BASE = "http://localhost:8001"

# 1. Index the repository (first time only)
httpx.post(f"{BASE}/index")

# 2. Get context using semantic search
context = httpx.post(f"{BASE}/context", json={
    "task": "Add retry logic to DynamoDB handler",
    "max_tokens": 30000,
    "include_docs": True
}).json()

print(f"Found {len(context['code_files'])} code files")
print(f"Found {len(context['doc_files'])} doc files")

# 3. Run multi-AI orchestration
result = httpx.post(f"{BASE}/orchestrate", json={
    "task": "Add exponential backoff retry logic",
    "include_docs": True
}).json()

print(f"Cost: ${result['costs']['this_request_usd']:.4f}")
print(f"Recommendation: {result['recommended_action']}")

# 4. Create PR with AI-generated code
workflow = httpx.post(f"{BASE}/workflow", json={
    "task": "Add retry logic",
    "files": {"src/handler.py": result['ai_responses'][0]['content']},
    "ai_provider": "claude"
}).json()

print(f"PR created: {workflow['pull_request']['url']}")
```

---

## RAG Pipeline Details

### Chunking Strategy

Files are split into chunks for embedding:

```
┌─────────────────────────────────────┐
│           Original File             │
│  (e.g., 5000 characters)            │
└─────────────────────────────────────┘
                 │
                 v
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Chunk 1 │ │ Chunk 2 │ │ Chunk 3 │
│ 1000chr │ │ 1000chr │ │ 1000chr │
│         │ │         │ │         │
│    ├────┼─┤ overlap │ │         │
│    │200 │ │   200   │ │         │
└────┴────┘ └─────────┘ └─────────┘
```

- **Chunk size**: 1000 characters (configurable)
- **Overlap**: 200 characters (prevents losing context at boundaries)
- **Minimum**: Chunks under 50 chars are skipped

### Embedding Generation

```python
# OpenAI (production)
embedder = OpenAIEmbeddings()  # 1536 dimensions
embeddings = embedder.embed(["code chunk 1", "code chunk 2"])

# Local (offline)
embedder = LocalEmbeddings()   # 384 dimensions
embeddings = embedder.embed(["code chunk 1", "code chunk 2"])
```

### Semantic Search

```python
# Search returns results sorted by cosine similarity
results = vs.search("authentication logic", limit=5)

# Each result includes:
# - path: File path
# - content: Chunk content
# - score: Similarity (0-1)
# - chunk_type: "code", "doc", "config", "test"
# - start_line, end_line: Location in file
```

---

## Cost Reference

**AI Providers** (per 1M tokens, late 2024):

| Provider | Input | Output |
|----------|-------|--------|
| Claude Sonnet | $3.00 | $15.00 |
| Claude Haiku | $0.25 | $1.25 |
| GPT-4 Turbo | $10.00 | $30.00 |
| GPT-4o | $5.00 | $15.00 |
| Bedrock Claude | $3.00 | $15.00 |

**Embeddings** (per 1M tokens):

| Provider | Cost |
|----------|------|
| OpenAI text-embedding-3-small | $0.02 |
| Local (sentence-transformers) | Free |

**Typical costs:**
- 3-AI pipeline: $0.05 - $0.10 per run
- Index 1000 files: ~$0.10 (OpenAI embeddings)

---

## Project Structure

```
github-mcp-server-v2/
├── src/
│   ├── api_v2.py                  # FastAPI endpoints
│   ├── config.py                  # Configuration
│   ├── context/
│   │   └── manager.py             # Context gathering (code + docs)
│   ├── orchestrator/
│   │   └── multi_ai.py            # Multi-AI pipeline + costs
│   ├── github/
│   │   ├── repo.py                # Repository operations
│   │   └── workflow.py            # Branch/commit/PR automation
│   ├── cost/
│   │   ├── __init__.py
│   │   └── tracker.py             # Cost tracking module
│   └── vectorstore/
│       ├── __init__.py
│       └── store.py               # Full RAG implementation
├── demo4/
│   ├── demo_full.py               # Full feature demo
│   ├── demo_vectorstore.py        # RAG pipeline demo
│   └── test_quick.py              # Quick endpoint test
├── sample-repo/                   # Sample codebase for testing
├── requirements.txt
├── .env.example
└── README.md
```

---

## Use Case: Enterprise AI Collaboration

**Scenario**: A team manages a 42MB AWS serverless codebase with 3GB of documentation. They use Claude for implementation, GPT for code review, and Amazon Q for AWS optimization.

**Before**: Manual copy/paste between tools, lost context, no cost tracking, manual PR creation.

**After with Demo #4**:

1. **RAG Pipeline**: Semantic search finds relevant code across 42MB
2. **Context**: Server selects relevant 30K tokens + discovers runbooks
3. **Orchestration**: All 3 AIs work with identical context
4. **Costs**: See exactly what each AI call costs ($0.055 typical)
5. **Automation**: AI suggestions become PRs automatically

---

## Demo Progression

| Demo | Features |
|------|----------|
| Demo #1 | Core MCP server, basic context |
| Demo #2 | Multi-AI orchestration |
| Demo #3 | AWS Bedrock integration |
| **Demo #4** | **RAG pipeline, GitHub workflow, enhanced context, cost tracking** |

---

## Key Technologies

| Component | Technology |
|-----------|------------|
| API Server | FastAPI + Uvicorn |
| Vector Database | ChromaDB |
| Embeddings | OpenAI / Sentence-Transformers |
| AI Providers | Anthropic, OpenAI, AWS Bedrock |
| GitHub Integration | PyGithub |
| Token Counting | tiktoken |

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python demo4/test_quick.py`
5. Submit a pull request

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

Built for AI infrastructure consulting, demonstrating how to coordinate multiple AI tools on enterprise codebases with semantic search, consistent context, and cost visibility.

**Demo #4** - Making AI collaboration practical for real engineering teams.