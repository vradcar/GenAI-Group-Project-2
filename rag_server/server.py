# rag_server/server.py
import typer
from rag_server.settings import get_rag_settings
from rag_server.retriever import Retriever

app = typer.Typer(help="Custom local RAG MCP server")

# Initialize settings and retriever once
settings = get_rag_settings()
retriever = Retriever(settings)

@app.command()
def serve():
    """
    Start the RAG MCP server.
    """
    typer.echo("RAG MCP server ready!")
    typer.echo(f"Collection: {settings.rag_collection}, Vector DB: {settings.rag_vector_dir}")
    typer.echo("You can now call the 'ask' command to query documents.")

@app.command()
def ask(question: str):
    """
    Query the RAG server and return an answer.
    """
    result = retriever.query(question)
    typer.echo("Question: " + result["question"])
    typer.echo("Answer: " + result["answer"])
    typer.echo("Retrieved Chunks:")
    for idx, chunk in enumerate(result["chunks"], 1):
        typer.echo(f"{idx}. {chunk[:300]}...")  # show first 300 chars

if __name__ == "__main__":
    app()