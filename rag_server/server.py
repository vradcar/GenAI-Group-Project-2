import typer
from rich import print

from rag_server.retriever import TemplateRetriever
from rag_server.settings import get_rag_settings

app = typer.Typer(help="Custom local RAG MCP server template")


@app.command()
def serve() -> None:
    settings = get_rag_settings()
    retriever = TemplateRetriever(settings)
    retriever.ensure_vector_store()
    print(
        "[green]RAG server template ready.[/green] "
        "Implement MCP protocol handlers and tool registration here."
    )


@app.command()
def ask(question: str) -> None:
    settings = get_rag_settings()
    retriever = TemplateRetriever(settings)
    result = retriever.query(question)
    print(result)


if __name__ == "__main__":
    app()
