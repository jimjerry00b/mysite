import os, sys, json, sqlite3, django, requests
from mcp.server.fastmcp import FastMCP

sys.path.insert(0, "/var/www/mysite")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
mcp = FastMCP("mysite")

@mcp.tool()
def list_api_routes() -> str:
    """List all URL routes in the Django project."""
    from django.urls import get_resolver
    routes = []
    def walk(pats, pre=""):
        for p in pats:
            if hasattr(p, "url_patterns"): walk(p.url_patterns, pre + str(p.pattern))
            else: routes.append(pre + str(p.pattern))
    walk(get_resolver().url_patterns)
    return json.dumps(routes, indent=2)

@mcp.tool()
def call_api(path: str, method: str = "GET", body: str = "") -> str:
    """Call the running mysite API, e.g. path='/mysite/api/health/'."""
    r = requests.request(method, "http://127.0.0.1" + path,
                         json=json.loads(body) if body else None, timeout=10)
    return f"HTTP {r.status_code}\n{r.text[:2000]}"

@mcp.tool()
def query_db(sql: str) -> str:
    """Run a read-only SELECT on the project database."""
    if not sql.strip().lower().startswith("select"):
        return "Only SELECT queries are allowed."
    conn = sqlite3.connect("file:/var/www/mysite/db.sqlite3?mode=ro", uri=True)
    try: return json.dumps(conn.execute(sql).fetchmany(50), default=str, indent=2)
    finally: conn.close()

if __name__ == "__main__":
    mcp.run()
