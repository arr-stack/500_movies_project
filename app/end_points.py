import uvicorn
from authx.exceptions import JWTDecodeError
from fastapi import FastAPI, Query, Response, HTTPException, Depends, Form
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from sqlalchemy import select, insert, join
from ItemORM import Session, MovieORM, User, Review
from evaluation import UserLogin, ReviewForm, UserLoginFake
from authx import AuthXConfig, AuthX, TokenPayload
import datetime
from typing import Annotated

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount('/static', StaticFiles(directory='static'), name='static')

TITLE_ = '500 movies'
YEAR_ = datetime.date.today().year

config = AuthXConfig()
config.JWT_SECRET_KEY = "yyyysayyyyy"
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=7)
secret = AuthX(config=config)


ITEMS_PER_PAGE = 10
TOTAL_PAGES = 50


async def optional_payload(request: Request):
    token_object = await secret.get_token_from_request(request)
    if not token_object:
        return None
    payload = TokenPayload.decode(
        token=token_object.token,
        key=config.JWT_SECRET_KEY
    )
    with Session() as session:
        return session.get(User, payload.sub)


@app.get("/")
def index(request: Request, page: int = Query(default=1, ge=1, le=TOTAL_PAGES), user: User | None = Depends(optional_payload)):
    offset_value = (page - 1) * ITEMS_PER_PAGE
    current_user = None
    if user:
        current_user = user
    with Session() as session:
        query = (
            select(MovieORM.id, MovieORM.title, MovieORM.original_title, MovieORM.year, MovieORM.description)
            .limit(ITEMS_PER_PAGE)
            .offset(offset_value))
        items = session.execute(query).all()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "items": items,
            "title": TITLE_,
            "year": YEAR_,
            "page": page,
            "total_pages": TOTAL_PAGES,
            'user': current_user,
        }
    )


@app.get('/movies/movie/{movie_id}')
def get_movie(request: Request, movie_id: int, user: User | None = Depends(optional_payload)):
    with Session() as session:
        data = session.get(MovieORM, movie_id)
        reviews = session.execute(select(
            Review.id,
            Review.user_id,
            User.username,
            Review.review_title,
            Review.review_body).join(User, Review.user_id == User.id).where(Review.movie_id == movie_id))
    return templates.TemplateResponse(request, "movie-page.html",
                                      {"movie": data, 'title': TITLE_, 'year': YEAR_, "reviews": reviews,
                                       "user": user})

@app.post("/movies/movie/reviews/create")
def create_review(form_data: Annotated[ReviewForm, Form()], payload: TokenPayload = Depends(secret.access_token_required)):
    current_user = payload.sub
    with Session() as session:
        new_review = Review(user_id=current_user, movie_id=form_data.movie_id, review_title=form_data.review_title, review_body=form_data.review_body)
        session.add(new_review)
        session.commit()
    return RedirectResponse(url=f"/movies/movie/{form_data.movie_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/reviews/delete")
def delete_review(review_id: int = Form(), movie_id: int = Form(), payload: TokenPayload = Depends(secret.access_token_required)):
    user_id = payload.sub
    with Session() as session:
        current_user = session.get(User, user_id)
        review = session.get(Review, review_id)
    if current_user.role == "user" and review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews")
    with Session() as session:
        session.delete(session.merge(review))
        session.commit()
    return RedirectResponse(url=f"/movies/movie/{movie_id}", status_code=status.HTTP_303_SEE_OTHER)

"""LOGIN/AUTH"""
@app.get('/login/sign_in')
def return_page(request: Request, user: User | None = Depends(optional_payload)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, 'log_in.html')

@app.get('/login/sign_up')
def return_page(request: Request, user: User | None = Depends(optional_payload)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, 'log_in.html')


@app.post("/login/sign_in")
def log_in(form_data: Annotated[UserLogin, Form()]): #def log_in(form_data: Annotated[UserLogin, Form()]):
    with Session() as session:
        result = select(User).where(User.email == form_data.email)
        data = session.scalars(result).first()
        if data and data.password == form_data.password:
            token = secret.create_access_token(uid=str(data.id))
            response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(
                key=config.JWT_ACCESS_COOKIE_NAME,
                value=token,
                samesite="lax",
                path='/',
                httponly=True,
                secure=False
            )
            return response
        else:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.post('/login/sign_up')
def sign_up(response: Response, form_data: Annotated[UserLogin, Form()]):
    with Session() as session:
        session.execute(insert(User).values(username=form_data.username, email=form_data.email, password=form_data.password, role='user'))
        session.commit()
        response.status_code = status.HTTP_303_SEE_OTHER
        return RedirectResponse(url='/')


#user pages
@app.get('/profiles/{user_id}')
def user_page(user_id: int, request: Request, user: User | None = Depends(optional_payload)):
    with Session() as session:
        user_info = session.get(User, user_id)
    return templates.TemplateResponse(request,'display-user.html', {'user_info': user_info, 'title': TITLE_, 'year': YEAR_,
                                       "user": user})

#search
@app.get('/search')
def search(request: Request, user: User | None = Depends(optional_payload)):
    return templates.TemplateResponse(request, 'search.html', {'title': TITLE_, 'year': YEAR_,
                                       "user": user})

@app.post('/search/{user_search}')
def get_movie(request: Request, user_search: str, user: User | None = Depends(optional_payload)):
    with Session() as session:
        result = session.execute(select(MovieORM.title, MovieORM.id))
        movies = [{'id': row.id, 'title': row.title} for row in result]
        movies.sort(key=lambda m: m['title'])

        left = 0
        right = len(movies) - 1

        while left <= right:
            middle = (left + right) // 2
            middle_item = movies[middle]
            if middle_item['title'] == user_search:
                return templates.TemplateResponse(request, 'search.html', {'item': middle_item, 'title': TITLE_, 'year': YEAR_,
                                       "user": user})
            elif middle_item['title'] < user_search:
                left = middle + 1
            else:
                right = middle - 1
    return templates.TemplateResponse(request, 'search.html', {'item': middle_item,'title': TITLE_, 'year': YEAR_,
                                       "user": user})


@app.post("/login/logout")
def log_out():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key=config.JWT_ACCESS_COOKIE_NAME, path="/")
    return response

@app.exception_handler(JWTDecodeError)
def handler(request: Request, exc: JWTDecodeError):
    response = RedirectResponse(url="/login/sign_in", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME, path="/")
    return response
#display user next show their username and link to their profile

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)