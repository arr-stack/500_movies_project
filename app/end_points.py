import uvicorn
from fastapi import FastAPI, Query, Response, HTTPException, Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy import select
from ItemORM import Session, MovieORM, User
from evaluation import UserLogin
from authx import AuthXConfig, AuthX
import datetime

app = FastAPI()

templates = Jinja2Templates(directory="templates")


config = AuthXConfig()
config.JWT_SECRET_KEY = "yyyysayyyyy"
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ['cookies']
secret = AuthX(config=config)


@app.get("/")
def index(request: Request):
    with Session() as session:
        items = session.execute(select(MovieORM.title, MovieORM.original_title, MovieORM.year, MovieORM.desc))
    return templates.TemplateResponse(request, "index.html", {"items": items, 'title': '500 movies',
                                                              'year': datetime.date.today().year})


@app.get('/movies')
def get_movies(request: Request, limit: int = Query(10, ge=1, le=50), offset: int = Query(0, ge=0)):
    with Session() as session:
        data = session.execute(select(MovieORM.title).offset(offset).limit(limit))
    return templates.TemplateResponse(request, "movie-page.html", {"data": data})

@app.get('/movies/movie/{movie_id}')
def get_movie(request: Request, movie_id: int):
    with Session() as session:
        result = select(MovieORM).where(MovieORM.id == movie_id)
        movie = session.scalars(result).first()
    return templates.TemplateResponse(request, "movie.html", {"movie": movie, 'site': '500 movies'})

"""LOGIN/AUTH"""
@app.get('/login/sign_in')
def return_page(request: Request):
    return templates.TemplateResponse(request, 'log_in.html')

@app.get('/login/sing_up')
def return_page(request: Request):
    return templates.TemplateResponse(request, 'sign_up.html')

@app.post("/login/sign_in")
def log_in(user_: UserLogin):
    with Session() as session:
        result = select(User).where(User.username == user_.username)
        data = session.scalars(result).first()
        if data and data.password == user_.password:
            token = secret.create_access_token(uid=str(data.id))
            response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
            return response
        else:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.post('login/sign_up')
def sign_up(username: str, email: str, password: str, response: Response):
    with Session() as session:
        session.execute(insert(User).values(username=username, email=email, password=password))
        session.commit()
        response.status_code = status.HTTP_303_SEE_OTHER
        return RedirectResponse(url='/')


#user pages
@app.get('/profiles/{user_id}', dependencies=[Depends(secret.access_token_required)])
def user_page(user_id: int, request: Request):
    with Session() as session:
        result = select(User).where(User.id == user_id)
        user_info = session.scalars(result).first()
    return templates.TemplateResponse(request,'display-user.html', {'user_info': user_info})

#search
@app.get('/search')
def search(request: Request):
    return templates.TemplateResponse(request, 'search.html', {'site': '500 movies'})

@app.post('/search/{user_search}')
def get_movie(user_search: str, request: Request):
    with Session() as session:
        result = session.execute(select(MovieORM.title, MovieORM.id))
        movies = [{'id': row.id, 'title': row.title} for row in result]
        print(movies)
        movies.sort(key=lambda m: m['title'])

        left = 0
        right = len(movies) - 1

        while left <= right:
            middle = (left + right) // 2
            middle_item = movies[middle]
            if middle_item['title'] == user_search:
                return templates.TemplateResponse(request, 'search.html', {'item': middle_item, 'site': '500 movies'})
            elif middle_item['title'] < user_search:
                left = middle + 1
            else:
                right = middle - 1
    return templates.TemplateResponse(request, 'search.html', {'item': middle_item, 'site': '500 movies'})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)