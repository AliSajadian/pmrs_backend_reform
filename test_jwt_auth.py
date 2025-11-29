#!/usr/bin/env python
"""
Quick test script for JWT authentication endpoints.

This script tests the basic JWT authentication flow:
1. Register a new user
2. Login with the user
3. Get user profile
4. Refresh the token
5. Change password
6. Logout

Usage:
    python test_jwt_auth.py
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'


def print_success(message):
    print(f"{GREEN}✓ {message}{END}")


def print_error(message):
    print(f"{RED}✗ {message}{END}")


def print_info(message):
    print(f"{BLUE}ℹ {message}{END}")


def print_warning(message):
    print(f"{YELLOW}⚠ {message}{END}")


def test_register():
    """Test user registration."""
    print_info("Testing user registration...")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    username = f"testuser_{timestamp}"
    
    data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        
        if response.status_code == 201:
            print_success("Registration successful")
            result = response.json()
            return username, result['access_token'], result['refresh_token']
        else:
            print_error(f"Registration failed: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return None, None, None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None, None, None


def test_login(username):
    """Test user login."""
    print_info("Testing login...")
    
    data = {
        "username": username,
        "password": "TestPass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        
        if response.status_code == 200:
            print_success("Login successful")
            result = response.json()
            print_info(f"Access token expires at: {datetime.fromtimestamp(result['access_expires_at'])}")
            print_info(f"User has {len(result['roles'])} role(s)")
            print_info(f"User has {len(result['all_permissions'])} permission(s)")
            return result['access_token'], result['refresh_token']
        else:
            print_error(f"Login failed: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return None, None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None, None


def test_profile(access_token):
    """Test getting user profile."""
    print_info("Testing get profile...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        
        if response.status_code == 200:
            print_success("Profile retrieved successfully")
            result = response.json()
            user = result['data']
            print_info(f"Username: {user['username']}")
            print_info(f"Email: {user['email']}")
            print_info(f"Full name: {user['full_name']}")
            return True
        else:
            print_error(f"Profile retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Profile error: {str(e)}")
        return False


def test_refresh(refresh_token):
    """Test token refresh."""
    print_info("Testing token refresh...")
    
    data = {
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/refresh", json=data)
        
        if response.status_code == 200:
            print_success("Token refreshed successfully")
            result = response.json()
            return result['access_token'], result['refresh_token']
        else:
            print_error(f"Token refresh failed: {response.status_code}")
            return None, None
    except Exception as e:
        print_error(f"Refresh error: {str(e)}")
        return None, None


def test_change_password(access_token):
    """Test password change."""
    print_info("Testing password change...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    data = {
        "old_password": "TestPass123!",
        "new_password": "NewTestPass456!",
        "new_password_confirm": "NewTestPass456!"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/auth/changePassword",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Password changed successfully")
            return True
        else:
            print_error(f"Password change failed: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return False
    except Exception as e:
        print_error(f"Password change error: {str(e)}")
        return False


def test_logout(access_token, refresh_token):
    """Test logout."""
    print_info("Testing logout...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    data = {
        "refresh_token": refresh_token,
        "logout_all": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Logout successful")
            return True
        else:
            print_error(f"Logout failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Logout error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("JWT Authentication Test Script")
    print("="*60 + "\n")
    
    # Test 1: Register
    print("\n" + "-"*60)
    print("Test 1: User Registration")
    print("-"*60)
    username, access_token, refresh_token = test_register()
    
    if not username:
        print_error("Cannot continue tests without successful registration")
        return
    
    # Test 2: Login
    print("\n" + "-"*60)
    print("Test 2: User Login")
    print("-"*60)
    access_token, refresh_token = test_login(username)
    
    if not access_token:
        print_error("Cannot continue tests without successful login")
        return
    
    # Test 3: Get Profile
    print("\n" + "-"*60)
    print("Test 3: Get User Profile")
    print("-"*60)
    test_profile(access_token)
    
    # Test 4: Refresh Token
    print("\n" + "-"*60)
    print("Test 4: Refresh Token")
    print("-"*60)
    new_access, new_refresh = test_refresh(refresh_token)
    
    if new_access:
        access_token = new_access
        refresh_token = new_refresh
    
    # Test 5: Change Password
    print("\n" + "-"*60)
    print("Test 5: Change Password")
    print("-"*60)
    password_changed = test_change_password(access_token)
    
    # If password was changed, login with new password
    if password_changed:
        print_info("Logging in with new password...")
        # This should fail with old password
        old_access, old_refresh = test_login(username)
        
        # Update password in our test
        print_warning("Update test to use new password for future logins")
    
    # Test 6: Logout
    print("\n" + "-"*60)
    print("Test 6: Logout")
    print("-"*60)
    test_logout(access_token, refresh_token)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print_success("All tests completed!")
    print_info("Check the output above for any failed tests")
    print("\n")


if __name__ == "__main__":
    main()

