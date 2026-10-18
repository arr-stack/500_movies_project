from pydantic import BaseModel, Field

class Movie(BaseModel):
    id: int = Field()
    title: str = Field(min_length=1)
    original_title: str = Field(min_length=1)
    year: int = Field()
    desc: str = Field()

class UserLogin(BaseModel):
    id: int = Field()
    email: str = Field()
    username: str = Field(min_length=1)
    password: str = Field(min_length=8)

