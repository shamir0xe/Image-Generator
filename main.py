import typer
from src.cmds.run_bot import app as image_generator
import logging

logging.basicConfig(level=logging.INFO)


app = typer.Typer(
    name="MoviePosterGen CLI", help="Generates set of cool posters from some movies"
)
app.add_typer(image_generator)

if __name__ == "__main__":
    app()
