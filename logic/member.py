from datetime import date, timedelta
from logic.book import Book

class Member:
    def __init__(self, name: str, member_id: int):
        self.name: str = name
        self.member_id: int = member_id
        self.borrowed_books: list[Book] = []
        self.MAX_BOOKS: int = 3
        self.fee_balance: float = 0

    def can_borrow_book (self):
        """
        Returns True, if member can still borrow books, otherwise False is returned.
        """
        return len(self.borrowed_books) < self.MAX_BOOKS
    
    def remove_book(self, isbn: str) -> bool:
        """
        Internal method to remove book with ISBN from borrowed list of member. Returns True, if success. If book with ISBN doesn't exist in list, False is returned. If two books with same ISBN exist, an exception is raised.
        """
        book_idxs = [idx for idx, book in enumerate(self.borrowed_books) if book.isbn == isbn]
        if len(book_idxs) == 0:
            return False
        elif len(book_idxs) > 1:
            raise Exception("Error: Books with same ISBN detected.")
        else:
            del self.borrowed_books[book_idxs[0]]
            return True
    
    def __str__(self) -> str:
        """
        Returns string representation of member with the books borrowed.
        """
        titles = ", ".join([book.title for book in self.borrowed_books])
        return f"{self.name} has following books borrowed: {titles if titles else 'No books'}"

    def __repr__(self) -> str:
        """
        Returns string representation of member for list display.
        """
        return f"Member {self.name}"
