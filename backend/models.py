from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str


class User(BaseModel):
    username: str
    bio: str

class QuizQuestion(BaseModel):
    id: int
    text: str
    options: list
    correct: str
