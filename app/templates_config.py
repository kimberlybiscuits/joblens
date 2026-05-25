import jinja2
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(
    env=jinja2.Environment(
        loader=jinja2.FileSystemLoader("app/templates"),
        autoescape=jinja2.select_autoescape(["html"]),
        cache_size=0,
    )
)
