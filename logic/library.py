from datetime import date, timedelta
from .date_simulation import DateSimulation
from .book import Book
from .member import Member
from .statistics import Statistics



class Library:
    DAILY_LATE_FEE: float = 0.5

    def __init__(self):
        self.books: list[Book] = []
        self.members: list['Member'] = []
    
    def get_statistics(self) -> Statistics:
        """
        Returns Statistics object with statistics about library.
        """
        stats = Statistics()

        # collect books and their total borrowed counts and sort from high to low
        books_and_counts = [(book, book.total_borrowed_count) for book in self.books]
        stats.books_total_borrowed_counts = sorted(books_and_counts, key=lambda x: x[1], reverse=True)

        # collect the count of currently borrowed books
        stats.books_currently_borrowed_count = len([book for book in self.books if book.is_available == False])

        # collect total count of books
        stats.books_total_count = len (self.books)

        # collect list of active users, having borrowed at least one book
        stats.active_members = [member for member in self.members if len(member.borrowed_books) > 0]

        return stats

    def register_member(self, member: 'Member') -> bool:
        """
        Registers new member in library and returns True upon success. If a member with same member id is already registered, False is returned.
        """
        members_same_id = [m for m in self.members if member.member_id == m.member_id]
        if len(members_same_id) > 0:
            return False
        self.members.append (member)
        return True

    def find_book(self, isbn: str) -> Book | None:
        """
        Finds a book by ISBN and returns it. If no book with this ISBN is found, None is returned. If multiple books with same ISBN is found, an exception is raised.
        """
        found_books = [book for book in self.books if book.isbn == isbn]
        if len(found_books) == 0:
            return None
        if len(found_books) > 1:
            raise Exception("Multiple Books with same ISBN found.")
        return found_books[0]

    def add_book(self, book: Book) -> bool:
        """
        Adds a book to the Library and returns True, if no book with this ISBN is in the library. If book with this ISBN already exists in the library, False is returned and book is not added.
        """
        if not self.find_book(book.isbn) is None:
            return False
        self.books.append(book)
        return True
    
    def list_books(self) -> str:
        """
        Returns the string representations of all the books in the library, separated with new lines.
        """
        books_string = ""
        for book in self.books:
            books_string = books_string + book.__str__() + "\n"
        return books_string
    
    def borrow_book(self, today: date, member: 'Member', isbn: str) -> bool:
        """
        Borrows a book with specified ISBN. Returns True, if this book exists in the library and can be borrowed. Otherwise, False is returned.
        """
        book = self.find_book(isbn)
        if book is None:
            return False
        return book.borrow(today, member)
    
    def _calculate_late_fee(self, today, isbn: str) -> float | None:
        """
        Calculates the late fee as of today for book with ISBN.
        """
        book = self.find_book(isbn)
        if not book:
            return None
        if not book.is_overdue(today):
            return 0.0
        overdue_days = today - book.due_date
        return round(overdue_days.days * Library.DAILY_LATE_FEE, 2)

    def return_book(self, today: date, isbn: str) -> tuple[bool, float | None]:
        """
        Returns a book with specified ISBN to the library. Method returns a tuple with True and with late fee, if library.return_book succeeds, otherwise False and None. If the wait list is not empty, the book is borrowed to the next member in the wait list.
        """
        book = self.find_book(isbn)
        if not book:
            return False, None
        late_fee = self._calculate_late_fee(today, isbn)
        success = book.return_book()

        # manage wait list and borrow book to next member if available
        if success and len(book.wait_list) > 0:
            next_member = book.wait_list[0]
            if next_member.can_borrow_book():
                success = next_member.borrow_book(today, self, isbn)
                if success:
                    book.wait_list.pop(0)
        return success, late_fee


if __name__ == "__main__":

    # Test setup
    date_sim = DateSimulation()
    lib = Library()
    b1 = Book ("Python Basics", "Anna", "123")
    b2 = Book ("Python Intermediate", "Ben", "456")
    b3 = Book ("Python Advanced", "Carla", "789")
    b4 = Book ("Git", "Dave", "321")

    assert lib.add_book(b1), "Error: Cannot add book."
    assert lib.add_book(b2), "Error: Cannot add book."
    assert lib.add_book(b3), "Error: Cannot add book."
    assert lib.add_book(b4), "Error: Cannot add book."

    m1 = Member("Eva", 0)
    m2 = Member("Fred", 1)

    # Test borrow book with wait list
    assert m1.borrow_book(date_sim.today, lib, "123"), "Error: Book b1 cannot be borrowed, even though it is available."
    assert not m2.borrow_book(date_sim.today, lib, "123"), "Error: Book b1 can be borrowed, even though it is not available." 

    print("------- Test Book: -----------")
    print(lib.find_book("123"))
    assert m2 in b1.wait_list, "Error: Member m2 not in wait list." 

    # Test m1.return_book with borrowing book to first member m2 in wait list
    assert m1.return_book(date_sim.today, lib, "123"), "Error: Book b1 cannot be returned, even though it is not available."
    assert not b1 in m1.borrowed_books, "Error: Book b1 still in borrowed books list of m1"
    assert b1 in m2.borrowed_books, "Error: Book b1 not added to borrowed books list of m2"
    assert not m2 in b1.wait_list, "Error: Member m2 still in wait list."

    # Test that member m2 has borrowed three books and thus cannot borrow book from waiting list, if m1 returns book.
    print("------- Members in Test: ----------")
    print(m1)
    print(m2) # m2 has already Python Basics borrowed, so borrow two more books for m2
    assert m2.borrow_book(date_sim.today,lib, "456"), "Error: Book b2 cannot be borrowed by m2, even though only 1 book borrowed and book is available."
    assert m2.borrow_book(date_sim.today,lib, "789"), "Error: Book b3 cannot be borrowed by m2, even though only 1 book borrowed and book is available."
    assert m1.borrow_book(date_sim.today,lib, "321"), "Error: Book b4 cannot be borrowed by m1, even though is available and m1 has less than three books borrowed."
    assert m1.return_book(date_sim.today, lib, "321"), "Error: m1 cannot return book b4, even though it is not available."
    assert not b4 in m2.borrowed_books, "Error: Book b4 was borrowed from waiting list to m2, even though m2 has already borrowed three books."

    # Test for Faelligkeitsdatum und Gebührensystem mit Simulation
    date_sim = DateSimulation()
    lib = Library()
    b1 = Book ("Python Basics", "Anna", "123")
    b2 = Book ("Python Intermediate", "Ben", "456")

    assert lib.add_book(b1), "Error: Cannot add book."
    assert lib.add_book(b2), "Error: Cannot add book."

    eva = Member("Eva", 0)
    eva.borrow_book(date_sim.today, lib, "123")
    date_sim.advance_date(7)
    eva.borrow_book(date_sim.today, lib, "456")
    date_sim.advance_date(8)
    assert b1.is_overdue(date_sim.today), "Error: Book b1 should be overdue."
    assert not b2.is_overdue(date_sim.today), "Error: Book b2 should not be overdue."
    assert eva.return_book(date_sim.today, lib, "123") and eva.fee_balance == 0.5, "Error: Overdue fee should be 0.5."
    assert eva.return_book(date_sim.today, lib, "456") and eva.fee_balance == 0.5, "Error: There should be no late fee."
    
    # Test library.register_member
    lib = Library()
    date_sim = DateSimulation()
    eva = Member("Eva", 0)
    fred = Member("Fred", 0)
    assert lib.register_member(eva), "Error: Eva should be registered."
    assert eva in lib.members, "Error: Eva should be in members list of library."
    assert not lib.register_member(fred), "Error: Fred should not be registered, as same member_id as already registered member Eva."
    assert len(lib.members) == 1, "Error: There should be only one registered member."
    fred = Member("Fred", 1)
    assert lib.register_member(fred), "Error: Fred should be registered."

    # ----------- Test statistics ---------------------

    # Test setup
    b1 = Book ("Python Basics", "Anna", "123")
    b2 = Book ("Python Intermediate", "Ben", "456")

    assert lib.add_book(b1), "Error: Cannot add book."
    assert lib.add_book(b2), "Error: Cannot add book."

    assert eva.borrow_book(date_sim.today, lib, "123"), "Error: borrow_book should succeed."
    assert fred.borrow_book(date_sim.today, lib, "456"), "Error: borrow_book should succeed."
    assert fred.return_book(date_sim.today, lib, "456"), "Error: return_book should succeed."
    assert eva.borrow_book(date_sim.today, lib, "456"), "Error: borrow_book should succeed."
    stats = lib.get_statistics()

    # stats test total borrowed counts of books
    assert stats.books_total_borrowed_counts[0][0].isbn == "456" and stats.books_total_borrowed_counts[0][1] == 2, "Error: Book with ISBN '456' should be first entry with total borrowed count 2."
    assert stats.books_total_borrowed_counts[1][0].isbn == "123" and stats.books_total_borrowed_counts[1][1] == 1, "Error: Book with ISBN'123' should be second entry with total borrowed count 1."
    assert len(stats.books_total_borrowed_counts) == 2, "Error: There should be only two books."

    # stats test total books currently borrowed
    assert stats.books_currently_borrowed_count == 2, "Error: Two books are currently borrowed."

    # stats test books total count
    assert stats.books_total_count == 2, "Error: There are currently two books in the library."

    # stats test active members, members that have currently books borrowed
    assert len (stats.active_members) == 1, "Error: There is one active member."
    assert stats.active_members[0] == eva, "Error: Eva is the only active member."