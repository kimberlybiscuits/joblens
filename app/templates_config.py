import jinja2
from starlette.templating import Jinja2Templates


def _dateformat(value):
    """Format a date or datetime to YYYY-MM-DD. Works with both strings and datetime objects."""
    if not value:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)[:10]


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("app/templates"),
    autoescape=jinja2.select_autoescape(["html"]),
    cache_size=0,
)
env.filters["dateformat"] = _dateformat

templates = Jinja2Templates(env=env)
