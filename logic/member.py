from datetime import date, timedelta
from logic.book import Book
from logic.library import Library

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

    def borrow_book(self, today: date, library: Library, isbn: str) -> bool:
        """
        Borrows book with ISBN from library and adds it to the borrowed books of the member. Returns True, if member has less than three books borrowed and if library.borrow_book succeeds. Otherwise, False.
        """

        if not self.can_borrow_book():
            return False
        success = library.borrow_book(today, self, isbn)
        if not success:
            return False
        book = library.find_book(isbn)
        if not book:
            return False
        self.borrowed_books.append(book)
        return True
    
    def _remove_book(self, isbn: str) -> bool:
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

    def return_book(self, today: date, library: Library, isbn: str) -> bool:
        """
        Returns book with ISBN to library and removes it from the borrowed books of the member. If the wait list of the bookis not empty, the book is borrowed to the next member in the wait list. Method returns True, if succeeds, otherwise False.
        """
        success, late_fee = library.return_book(today, isbn)
        if not success:
            return False
        success = self._remove_book(isbn)

        if late_fee:
            self.fee_balance += late_fee
        return success
    
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
