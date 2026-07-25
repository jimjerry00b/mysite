from django.http import HttpResponse


def home(request):
    """Simple landing page for the site root."""
    html = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>mysite</title>
    <style>
        body { font-family: system-ui, sans-serif; margin: 4rem auto; max-width: 40rem;
               padding: 0 1rem; line-height: 1.6; color: #222; }
        code { background: #f4f4f4; padding: .1rem .3rem; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>mysite</h1>
    <p>The site is running. Deployed automatically via the GitHub Actions CI/CD pipeline.</p>
    <p>Admin: <a href="admin/">/mysite/admin/</a></p>
</body>
</html>"""
    return HttpResponse(html)
