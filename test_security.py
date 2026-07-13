from app.services.security import hash_password, verify_password

password = "Tarika@123"

hashed = hash_password(password)

print("Original Password :", password)
print("Hashed Password   :", hashed)

print("\nVerification Test")

print(
    verify_password(
        "Tarika@123",
        hashed
    )
)

print(
    verify_password(
        "wrongpassword",
        hashed
    )
)