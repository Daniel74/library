from datetime import date, timedelta
from .member import Member

class Book:
    LOAN_DURATION_DAYS: int = 14

    def __init__(self, title: str, author: str, isbn: str):
        self.title: str = title
        self.author: str = author
        self.isbn: str = isbn
        self.is_available: bool = True
        self.wait_list: list = []
        self.due_date: date | None = None
        self.total_borrowed_count: int = 0
    
    def borrow(self, today: date, member: 'Member') -> bool:
        """
        Returns True, if book is available and can be borrowed. False is returned if book is not availabe and cannot be borrowed. In this case, the member is stored in the wait list of the book.
        """
        if not self.is_available:
            self.wait_list.append(member)
            return False
        
        self.is_available = False 
        self.total_borrowed_count += 1       
        self.due_date = today + timedelta(days=Book.LOAN_DURATION_DAYS)
        return True
    
    def is_overdue(self, today: date) -> bool | None:
        """
        Returns True, if today is after the due date of the book. If this is not the case, or due date is None, False is returned.
        """
        if not self.due_date:
            return False
        return today > self.due_date
    
    def return_book(self) -> bool:
        """
        Returns True, if book is not available, thus can be returned. If book is already available, it cannot be returned and False is returned.
        """
        if self.is_available:
            return False
        self.is_available = True
        self.due_date = None
        return True
    
    def __str__(self) -> str:
        """
        Returns string representation of book.
        """
        return f"Book with title {self.title}, from author {self.author}, and ISBN {self.isbn} is {'available' if self.is_available else 'borrowed'}.\nThe wait list is {self.wait_list}.\nDue Date is {self.due_date}."
