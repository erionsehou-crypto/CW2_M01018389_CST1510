import bcrypt
import os

# -----------------------------
#  Global constant
# -----------------------------
USER_DATA_FILE = "users.txt"


# -----------------------------
#  Core security functions
# -----------------------------
def hash_password(plain_text_password):
    """
    Hashes a password using bcrypt with automatic salt generation.

    Args:
        plain_text_password (str): The plaintext password to hash.

    Returns:
        str: The hashed password as a UTF-8 string.
    """
    # Encode the password to bytes
    password_bytes = plain_text_password.encode("utf-8")

    # Generate salt
    salt = bcrypt.gensalt()

    # Hash the password
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return hash as normal string for storage in file
    return hashed.decode("utf-8")


def verify_password(plain_text_password, hashed_password):
    """
    Verifies a plaintext password against a stored bcrypt hash.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    password_bytes = plain_text_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# -----------------------------
#  User management functions
# -----------------------------
def user_exists(username):
    """
    Checks if a username already exists in users.txt

    Returns:
        bool
    """
    # If the file does not exist yet, there are no users
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            stored_username = line.split(",")[0]
            if stored_username == username:
                return True

    return False


def register_user(username, password):
    """
    Registers a new user by hashing password and storing credentials.
    Format in file: username,hashed_password

    Returns:
        bool: True if success, False if username exists
    """
    if user_exists(username):
        return False

    hashed = hash_password(password)

    with open(USER_DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username},{hashed}\n")

    return True


def login_user(username, password):
    """
    Authenticates a user by verifying username and password.

    Returns:
        bool
    """
    if not os.path.exists(USER_DATA_FILE):
        print("Error: No users are registered yet.")
        return False

    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            stored_username, stored_hash = line.split(",", 1)

            if stored_username == username:
                # Found the username: verify password
                if verify_password(password, stored_hash):
                    print(f"Success: Welcome, {username}!")
                    return True
                else:
                    print("Error: Invalid password.")
                    return False

    # Username not found
    print("Error: Username not found.")
    return False


# -----------------------------
#  Input validation
# -----------------------------
def validate_username(username):
    """
    Validates username format.

    Returns:
        (bool, str): (is_valid, error_message)
    """
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters."
    if not username.isalnum():
        return False, "Username must contain only letters and numbers."
    return True, ""


def validate_password(password):
    """
    Validates password strength.

    Returns:
        (bool, str): (is_valid, error_message)
    """
    if len(password) < 6 or len(password) > 50:
        return False, "Password must be between 6 and 50 characters."

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not (has_upper and has_lower and has_digit):
        return False, "Password must include uppercase, lowercase and a digit."

    return True, ""


# -----------------------------
#  Menu / main loop
# -----------------------------
def display_menu():
    """Displays the main menu options."""
    print("\n" + "=" * 50)
    print("  MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print("  Secure Authentication System")
    print("=" * 50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)


def main():
    """Main program loop."""
    print("\nWelcome to the Multi-Domain Intelligence Authentication Module")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == "1":
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()

            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            if register_user(username, password):
                print(f"Success: User '{username}' registered successfully!")
            else:
                print(f"Error: Username '{username}' already exists.")

        elif choice == "2":
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # login_user prints appropriate messages
            login_user(username, password)
            input("\nPress Enter to return to main menu...")

        elif choice == "3":
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
