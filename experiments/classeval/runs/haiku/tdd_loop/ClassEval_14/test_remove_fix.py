import os
from solution import BookManagementDB

# Clean up any existing test database
if os.path.exists("verify_test.db"):
    os.remove("verify_test.db")

# Create a fresh database instance
book_db = BookManagementDB("verify_test.db")

# Add two books
book_db.add_book('book1', 'author1')
book_db.add_book('book2', 'author2')

# Check initial count
books_before = book_db.search_books()
print(f"Books before removal: {books_before}")
print(f"Count before: {len(books_before)}")

# Remove the first book
book_db.remove_book(1)

# Check count after removal
books_after = book_db.search_books()
print(f"Books after removal: {books_after}")
print(f"Count after: {len(books_after)}")

# Verify the test passes
if len(books_before) == 2 and len(books_after) == 1:
    print("✓ Test PASSED: remove_book correctly deleted the book")
else:
    print("✗ Test FAILED: remove_book did not work as expected")

# Clean up
os.remove("verify_test.db")
