#!/usr/bin/env bash
set -euo pipefail

# Parse flags
SKIP_BOOTSTRAP=false
SKIP_TESTS=false
SKIP_RAG_INGEST=false
SKIP_MCP_CHECK=false

for arg in "$@"; do
  case "$arg" in
    --skip-bootstrap)  SKIP_BOOTSTRAP=true ;;
    --skip-tests)      SKIP_TESTS=true ;;
    --skip-rag-ingest) SKIP_RAG_INGEST=true ;;
    --skip-mcp-check)  SKIP_MCP_CHECK=true ;;
    *) echo "Unknown flag: $arg"; exit 1 ;;
  esac
done

# Navigate to repo root (parent of scripts/mac/)
cd "$(dirname "$0")/../.."

echo "[Deploy] Starting local deployment checks..."

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example to .env and set API keys before deployment." >&2
  exit 1
fi

if [ "$SKIP_BOOTSTRAP" = false ]; then
  echo "[Deploy] Bootstrapping environment..."
  bash scripts/mac/bootstrap.sh
fi

if [ "$SKIP_TESTS" = false ]; then
  echo "[Deploy] Running tests..."
  bash scripts/mac/run_tests.sh
fi

if [ "$SKIP_RAG_INGEST" = false ]; then
  echo "[Deploy] Running RAG ingestion..."
  bash scripts/mac/run_rag_ingest.sh
fi

if [ "$SKIP_MCP_CHECK" = false ]; then
  echo "[Deploy] Running MCP connectivity and invocation checks..."
  export PYTHONPATH="src"

  TMP_SCRIPT=$(mktemp "${TMPDIR:-/tmp}/deploy_mcp_check.XXXXXX.py")
  cat > "$TMP_SCRIPT" << 'PYTHON_EOF'
import asyncio
from forgepilot.mcp_client import MCPClient

async def main():
    client = MCPClient('configs/mcp.servers.example.json')
    async with client:
        servers = client.list_servers()
        print('servers:', servers)

        required = {'filesystem', 'rag', 'context7'}
        missing = sorted(required - set(servers))
        if missing:
            raise RuntimeError(f"Missing MCP servers: {missing}")

        fs = await client.call_tool('filesystem__read_file', {'path': 'README.md'})
        rag = await client.call_tool('rag__rag_health', {})
        ctx = await client.call_tool('context7__resolve-library-id', {
            'query': 'How to build RAG with LangChain?',
            'libraryName': 'langchain'
        })

        for name, result in [('filesystem', fs), ('rag', rag), ('context7', ctx)]:
            if not result.get('success'):
                raise RuntimeError(f"{name} MCP call failed: {result.get('error')}")

        print('filesystem/rag/context7 MCP calls: OK')

asyncio.run(main())
PYTHON_EOF

  python3 "$TMP_SCRIPT"
  rm -f "$TMP_SCRIPT"
fi

echo "[Deploy] Local deployment checks completed successfully."
