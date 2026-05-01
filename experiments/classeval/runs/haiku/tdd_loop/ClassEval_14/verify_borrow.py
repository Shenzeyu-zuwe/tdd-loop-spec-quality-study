from solution import BookManagementDB
import os

# Clean up any existing test db
if os.path.exists("verify_borrow.db"):
    os.remove("verify_borrow.db")

# Test borrow_book functionality
book_db = BookManagementDB("verify_borrow.db")
book_db.add_book('Test Book', 'Test Author')

# Check initial availability (should be 1)
books = book_db.search_books()
print(f"Before borrow: {books}")
assert books[0][3] == 1, f"Initial availability should be 1, got {books[0][3]}"

# Borrow the book
book_db.borrow_book(1)

# Check availability after borrow (should be 0)
books = book_db.search_books()
print(f"After borrow: {books}")
assert books[0][3] == 0, f"After borrow, availability should be 0, got {books[0][3]}"

print("PASS: borrow_book test passed!")
