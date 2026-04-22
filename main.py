from fastapi import FastAPI
from logic.library import Library

app = FastAPI()
lib = Library()

@app.get("/books")
def get_books():
    pass