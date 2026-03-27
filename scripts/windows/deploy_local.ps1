param(
  [switch]$SkipBootstrap,
  [switch]$SkipTests,
  [switch]$SkipRagIngest,
  [switch]$SkipMcpCheck
)

$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..\..

Write-Host "[Deploy] Starting local deployment checks..."

if (-not (Test-Path .\.env)) {
  throw "Missing .env. Copy .env.example to .env and set API keys before deployment."
}

if (-not $SkipBootstrap) {
  Write-Host "[Deploy] Bootstrapping environment..."
  .\scripts\windows\bootstrap.ps1
}

if (-not $SkipTests) {
  Write-Host "[Deploy] Running tests..."
  .\scripts\windows\run_tests.ps1
}

if (-not $SkipRagIngest) {
  Write-Host "[Deploy] Running RAG ingestion..."
  .\scripts\windows\run_rag_ingest.ps1
}

if (-not $SkipMcpCheck) {
  Write-Host "[Deploy] Running MCP connectivity and invocation checks..."
  $env:PYTHONPATH = "src"

  $script = @'
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
'@

  Set-Content -Path .\tmp_deploy_mcp_check.py -Value $script
  python .\tmp_deploy_mcp_check.py
  Remove-Item .\tmp_deploy_mcp_check.py -Force
}

Write-Host "[Deploy] Local deployment checks completed successfully."
