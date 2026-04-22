from book import Book
from .member import Member

class Statistics:
    def __init__(self):
        self.books_total_borrowed_counts: list[tuple[Book, int]] = []
        self.books_currently_borrowed_count = 0
        self.books_total_count = 0
        self.active_members: list[Member] = []