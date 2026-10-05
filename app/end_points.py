import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

items = [
    {
        "id": 1,
        "name": "Merry"},
    {
        "id": 2,
        "name": "Renko"},
]


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"items": items, 'title': 'Good'})

@app.get('/search={search_str}')
def search(request: Request, search_str: str):
    #get from db using search_str
    return templates.TemplateResponse(request, "search.html")
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)