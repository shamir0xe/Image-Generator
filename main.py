import typer
from src.cmds.run_bot import main

app = typer.Typer(
    name="MoviePosterGen CLI", help="Generates set of cool posters from some movies"
)
app.command(name="run-bot")(main)

if __name__ == "__main__":
    app()
