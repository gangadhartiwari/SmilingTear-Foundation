import sqlite3
from werkzeug.security import generate_password_hash

username = "admin"
email = "smilingtearsfoundation@gmail.com"
password = "admin@stf17"  # new password
role = "admin"

conn = sqlite3.connect("smilingtears.db")
cur = conn.cursor()

# Update password for existing admin
cur.execute("""
    UPDATE users
    SET password = ?
    WHERE email = ?
""", (generate_password_hash(password), email))

conn.commit()
conn.close()

print("Admin password updated successfully!")
