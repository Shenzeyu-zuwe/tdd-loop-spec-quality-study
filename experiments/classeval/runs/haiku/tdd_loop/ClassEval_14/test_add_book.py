from solution import BookManagementDB
import os

# Clean up any existing test database
if os.path.exists("test_add_book.db"):
    os.remove("test_add_book.db")

# Test case 1: Add single book and verify it was inserted
book_db = BookManagementDB("test_add_book.db")
book_db.create_table()
book_db.add_book('book1', 'author')

# Verify the book was added
result = book_db.search_books()
print(f"Test 1 - After adding one book: {result}")
assert len(result) == 1, f"Expected 1 book, got {len(result)}"
assert result[0][1] == 'book1', f"Expected title 'book1', got '{result[0][1]}'"
assert result[0][2] == 'author', f"Expected author 'author', got '{result[0][2]}'"
assert result[0][3] == 1, f"Expected availability 1, got {result[0][3]}"
print("Test 1 PASSED\n")

# Test case 2: Add multiple books
book_db.add_book('book2', 'author2')
book_db.add_book('book3', 'author3')

result = book_db.search_books()
print(f"Test 2 - After adding three books: {result}")
assert len(result) == 3, f"Expected 3 books, got {len(result)}"
assert result[1][1] == 'book2', f"Expected title 'book2', got '{result[1][1]}'"
assert result[2][1] == 'book3', f"Expected title 'book3', got '{result[2][1]}'"
print("Test 2 PASSED\n")

print("All tests passed!")

# Clean up
book_db.connection.close()
os.remove("test_add_book.db")
