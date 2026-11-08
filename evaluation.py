from pydantic import BaseModel, Field

class ReviewForm(BaseModel):
    movie_id: str = Field()
    review_title: str = Field(min_length=1)
    review_body: str = Field(min_length=1)

class UserLogin(BaseModel):
    id: int = Field()
    email: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=8)
    role: str = Field(min_length=1)

class UserLoginFake(BaseModel):
    password: str = Field()
    email: str = Field()

