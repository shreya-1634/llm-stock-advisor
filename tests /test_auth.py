# your_project/tests/test_auth.py

import pytest
from unittest.mock import MagicMock, patch

# Adjust imports based on your exact project structure
# Assuming AuthManager, UserManager, PasswordUtils, EmailUtils are importable
from auths.auth import AuthManager
from db.user_manager import UserManager
from utils.password_utils import PasswordUtils
from utils.email_utils import EmailUtils
from utils.session_utils import SessionManager # If AuthManager interacts with session_manager

# --- Pytest Fixtures (Setup for tests) ---

@pytest.fixture
def mock_user_manager():
    """Mocks the UserManager to control database interactions."""
    manager = MagicMock(spec=UserManager)
    # Configure mock behavior:
    manager.get_user_by_email.return_value = None # Default: no user found
    manager.add_user.return_value = True # Default: user added successfully
    manager.store_otp.return_value = True # Default: OTP stored successfully
    manager.verify_otp.return_value = False # Default: OTP verification fails
    manager.set_email_verified.return_value = True
    manager.update_user_password.return_value = True
    # Add _log_activity as a mock to prevent errors
    manager._log_activity = MagicMock()
    return manager

@pytest.fixture
def mock_password_utils():
    """Mocks PasswordUtils for hashing and verification."""
    utils = MagicMock(spec=PasswordUtils)
    utils.hash_password.return_value = "hashed_password_mock"
    utils.verify_password.return_value = True # Default: passwords match
    return utils

@pytest.fixture
def mock_email_utils():
    """Mocks EmailUtils for email sending and OTP generation."""
    utils = MagicMock(spec=EmailUtils)
    utils.generate_otp.return_value = "123456"
    utils.send_verification_email.return_value = True
    utils.send_password_reset_email.return_value = True
    return utils

@pytest.fixture
def mock_session_manager():
    """Mocks SessionManager for Streamlit session state interactions."""
    manager = MagicMock(spec=SessionManager)
    manager.is_logged_in.return_value = False # Default: not logged in
    manager.login_user = MagicMock()
    manager.logout_user = MagicMock()
    manager.get_current_user_email.return_value = "test@example.com"
    manager.get_current_user_role.return_value = "free"
    manager.has_permission.return_value = True # Default for testing purposes
    return manager


@pytest.fixture
def auth_manager(mock_user_manager, mock_password_utils, mock_email_utils, mock_session_manager):
    """Provides an AuthManager instance with mocked dependencies."""
    # Temporarily replace the real dependencies with mocks for AuthManager's initialization
    with patch('auths.auth.UserManager', return_value=mock_user_manager), \
         patch('auths.auth.PasswordUtils', return_value=mock_password_utils), \
         patch('auths.auth.EmailUtils', return_value=mock_email_utils), \
         patch('auths.auth.SessionManager', return_value=mock_session_manager):
        # We need to mock st.experimental_rerun() because it's called in login_ui
        with patch('streamlit.experimental_rerun'):
            yield AuthManager()


# --- Test Cases ---

def test_signup_success(auth_manager, mock_user_manager, mock_email_utils, mock_password_utils):
    """Test successful user signup."""
    # Simulate Streamlit input fields
    with patch('streamlit.text_input', side_effect=["test@example.com", "password123", "password123"]), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.success') as mock_st_success, \
         patch('streamlit.error') as mock_st_error, \
         patch('streamlit.session_state', new_callable=dict) as mock_session_state: # Mock session_state
        
        # Call the signup UI function (which contains the logic)
        auth_manager.signup_ui()

        # Assertions
        mock_user_manager.add_user.assert_called_once_with("test@example.com", "hashed_password_mock", role='free')
        mock_user_manager.store_otp.assert_called_once()
        mock_email_utils.send_verification_email.assert_called_once_with("test@example.com", "123456")
        mock_st_success.assert_called_once_with("Account created! Check your email for a verification OTP.")
        mock_st_error.assert_not_called()
        assert mock_session_state['signup_email_for_verification'] == "test@example.com"

def test_signup_password_mismatch(auth_manager, mock_user_manager, mock_st_error):
    """Test signup with mismatched passwords."""
    with patch('streamlit.text_input', side_effect=["test@example.com", "password123", "different_password"]), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.error') as mock_st_error:
        auth_manager.signup_ui()
        mock_st_error.assert_called_once_with("Passwords do not match.")
        mock_user_manager.add_user.assert_not_called() # Should not try to add user

# Add more signup tests: email already exists, weak password, missing fields etc.

def test_verify_email_success(auth_manager, mock_user_manager):
    """Test successful email verification."""
    test_email = "verify@example.com"
    mock_user_manager.get_user_by_email.return_value = {"email": test_email, "is_verified": False}
    mock_user_manager.verify_otp.return_value = True # Simulate correct OTP
    
    with patch('streamlit.text_input', return_value="123456"), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.success') as mock_st_success, \
         patch('streamlit.session_state', new_callable=dict) as mock_session_state:
        
        mock_session_state['signup_email_for_verification'] = test_email # Simulate email set by signup
        auth_manager.verify_email_ui(test_email)

        mock_user_manager.verify_otp.assert_called_once_with(test_email, "123456")
        mock_user_manager.set_email_verified.assert_called_once_with(test_email, True)
        mock_st_success.assert_called_once_with("Email verified successfully! You can now log in.")
        assert 'signup_email_for_verification' not in mock_session_state # Email should be cleared

# Add more verification tests: invalid OTP, expired OTP, already verified etc.

def test_login_success(auth_manager, mock_user_manager, mock_session_manager):
    """Test successful user login."""
    test_email = "login@example.com"
    mock_user_manager.get_user_by_email.return_value = {"email": test_email, "password_hash": "hashed_password_mock", "is_verified": True, "role": "free"}
    
    with patch('streamlit.text_input', side_effect=[test_email, "correct_password"]), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.error') as mock_st_error, \
         patch('streamlit.experimental_rerun'): # Mock rerun to prevent actual app reload
        
        auth_manager.login_ui()

        mock_session_manager.login_user.assert_called_once_with(test_email, "free")
        mock_user_manager._log_activity.assert_called_once_with(test_email, "login", "Successful login.")
        mock_st_error.assert_not_called()

def test_login_invalid_password(auth_manager, mock_user_manager, mock_password_utils):
    """Test login with incorrect password."""
    test_email = "login@example.com"
    mock_user_manager.get_user_by_email.return_value = {"email": test_email, "password_hash": "hashed_password_mock", "is_verified": True, "role": "free"}
    mock_password_utils.verify_password.return_value = False # Simulate incorrect password

    with patch('streamlit.text_input', side_effect=[test_email, "wrong_password"]), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.error') as mock_st_error:
        
        auth_manager.login_ui()

        mock_st_error.assert_called_once_with("Invalid email or password.")
        mock_user_manager._log_activity.assert_called_once_with(test_email, "login_failed", "Invalid password.")

# Add more login tests: unverified email, email not found, missing fields etc.

# --- Password Reset Tests ---
def test_reset_password_request_success(auth_manager, mock_user_manager, mock_email_utils):
    """Test successful request for password reset OTP."""
    test_email = "reset@example.com"
    mock_user_manager.get_user_by_email.return_value = {"email": test_email}
    
    with patch('streamlit.text_input', return_value=test_email), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.success') as mock_st_success, \
         patch('streamlit.experimental_rerun'), \
         patch('streamlit.session_state', new_callable=dict) as mock_session_state:
        
        auth_manager.reset_password_ui()

        mock_user_manager.store_otp.assert_called_once_with(test_email, "123456")
        mock_email_utils.send_verification_email.assert_called_once_with(test_email, "123456")
        mock_st_success.assert_called_once_with("A password reset OTP has been sent to your email.")
        assert mock_session_state['reset_email_sent'] is True
        assert mock_session_state['reset_token_email'] == test_email

def test_reset_password_set_new_password_success(auth_manager, mock_user_manager, mock_password_utils):
    """Test successful setting of new password after OTP verification."""
    test_email = "reset@example.com"
    mock_user_manager.verify_otp.return_value = True # Simulate correct OTP
    mock_user_manager.update_user_password.return_value = True

    with patch('streamlit.text_input', side_effect=["123456", "newpassword123", "newpassword123"]), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.success') as mock_st_success, \
         patch('streamlit.experimental_rerun'), \
         patch('streamlit.session_state', new_callable=dict) as mock_session_state:
        
        mock_session_state['reset_email_sent'] = True # Simulate previous request
        mock_session_state['reset_token_email'] = test_email
        
        auth_manager.reset_password_ui()

        mock_user_manager.verify_otp.assert_called_once_with(test_email, "123456")
        mock_password_utils.hash_password.assert_called_once_with("newpassword123")
        mock_user_manager.update_user_password.assert_called_once_with(test_email, "hashed_password_mock")
        mock_st_success.assert_called_once_with("Your password has been reset successfully. You can now log in.")
        assert 'reset_email_sent' not in mock_session_state # Session state should be cleaned up
        assert 'reset_token_email' not in mock_session_state
