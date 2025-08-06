"""
Test utilities for secure password generation and other common test functionality.
"""
import secrets
import string


def generate_test_password():
    """Generate a secure test password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(12)) + '123'