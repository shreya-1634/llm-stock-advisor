# your_project/auths/auth.py

import streamlit as st
import time
from db.user_manager import UserManager # <-- IMPORT FIXED
from utils.password_utils import PasswordUtils
from utils.email_utils import EmailUtils
from utils.session_utils import SessionManager # <-- IMPORT FIXED

class AuthManager:
    def __init__(self):
        self.user_manager = UserManager()
        self.password_utils = PasswordUtils()
        self.email_utils = EmailUtils()
        self.session_manager = SessionManager()

    def signup_ui(self):
        """Renders the user signup form and handles registration logic."""
        st.subheader("Create a New Account")
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email_input").strip()
            password = st.text_input("Password", type="password", key="signup_password_input")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password_input")
            submit_button = st.form_submit_button("Sign Up")

            if submit_button:
                if not email or not password or not confirm_password:
                    st.error("All fields are required.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6: # Basic password policy
                    st.error("Password must be at least 6 characters long.")
                elif self.user_manager.get_user_by_email(email):
                    st.error("Email already registered. Please log in or reset password.")
                else:
                    hashed_password = self.password_utils.hash_password(password)
                    otp = self.email_utils.generate_otp()
                    
                    if self.user_manager.add_user(email, hashed_password, role='free'):
                        if self.user_manager.store_otp(email, otp):
                            if self.email_utils.send_verification_email(email, otp):
                                st.success("Account created! Check your email for a verification OTP.")
                                st.session_state['signup_email_for_verification'] = email # Store email for next step
                            else:
                                st.error("Account created, but failed to send verification email. Please try 'Resend OTP'.")
                                st.session_state['signup_email_for_verification'] = email
                        else:
                            st.error("Failed to store OTP. Please try again.")
                    else:
                        st.error("Registration failed. Please try again.")
        
        # Display OTP verification section after signup
        if 'signup_email_for_verification' in st.session_state and st.session_state['signup_email_for_verification']:
            self.verify_email_ui(st.session_state['signup_email_for_verification'])


    def verify_email_ui(self, email_for_verification: str):
        st.subheader(f"Verify Email for {email_for_verification}")
        user_data = self.user_manager.get_user_by_email(email_for_verification)

        if not user_data or user_data.get('is_verified'):
            st.info("Email already verified or user not found.")
            if 'signup_email_for_verification' in st.session_state:
                del st.session_state['signup_email_for_verification']
            return

        with st.form("verify_email_form"):
            otp_input = st.text_input("Enter OTP", key="verify_otp_input").strip()
            col1, col2 = st.columns(2)
            with col1:
                verify_button = st.form_submit_button("Verify")
            with col2:
                resend_otp_button = st.form_submit_button("Resend OTP")

            if verify_button:
                if self.user_manager.verify_otp(email_for_verification, otp_input):
                    self.user_manager.set_email_verified(email_for_verification, True)
                    st.success("Email verified successfully! You can now log in.")
                    if 'signup_email_for_verification' in st.session_state:
                        del st.session_state['signup_email_for_verification']
                else:
                    st.error("Invalid OTP or OTP expired. Please try again or resend.")

            if resend_otp_button:
                otp = self.email_utils.generate_otp()
                if self.user_manager.store_otp(email_for_verification, otp):
                    if self.email_utils.send_verification_email(email_for_verification, otp):
                        st.success("New OTP sent to your email.")
                    else:
                        st.error("Failed to send new OTP. Please check email config.")
                else:
                    st.error("Failed to generate/store new OTP.")

    def login_ui(self):
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email_input").strip()
            password = st.text_input("Password", type="password", key="login_password_input")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                if not email or not password:
                    st.error("Please enter email and password.")
                    return

                user_data = self.user_manager.get_user_by_email(email)
                if user_data:
                    if self.password_utils.verify_password(password, user_data['password_hash']):
                        if user_data.get('is_verified', False):
                            self.session_manager.login_user(user_data['email'], user_data['role'])
                            self.user_manager._log_activity(email, "login", "Successful login.")
                            st.success("Logged in successfully!")
                            st.rerun() # <--- FIXED
                        else:
                            st.warning("Please verify your email first to log in.")
                            st.session_state['signup_email_for_verification'] = email
                    else:
                        st.error("Invalid email or password.")
                        self.user_manager._log_activity(email, "login_failed", "Invalid password.")
                else:
                    st.error("Invalid email or password.")
                    self.user_manager._log_activity(email, "login_failed", "Email not found.")

    def reset_password_ui(self):
        st.subheader("Reset Your Password")
        if 'reset_email_sent' not in st.session_state:
            st.session_state['reset_email_sent'] = False
        if 'reset_token_email' not in st.session_state:
            st.session_state['reset_token_email'] = None

        if not st.session_state['reset_email_sent']:
            st.info("Enter your email address to receive a password reset OTP.")
            with st.form("request_reset_form"):
                email = st.text_input("Email", key="reset_request_email").strip()
                request_button = st.form_submit_button("Send Reset OTP")

                if request_button:
                    user_data = self.user_manager.get_user_by_email(email)
                    if user_data:
                        otp = self.email_utils.generate_otp()
                        if self.user_manager.store_otp(email, otp):
                            if self.email_utils.send_verification_email(email, otp):
                                st.success("A password reset OTP has been sent to your email.")
                                st.session_state['reset_email_sent'] = True
                                st.session_state['reset_token_email'] = email
                                st.rerun()
                            else:
                                st.error("Failed to send reset OTP. Please try again.")
                        else:
                            st.error("Failed to store reset OTP. Please try again.")
                    else:
                        st.error("Email not found.")
        else:
            st.info(f"Enter the OTP sent to {st.session_state['reset_token_email']} and your new password.")
            with st.form("reset_password_form"):
                otp_input = st.text_input("Enter OTP", key="reset_otp_input").strip()
                new_password = st.text_input("New Password", type="password", key="new_password_input")
                confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password_input")
                reset_button = st.form_submit_button("Reset Password")

                if reset_button:
                    email = st.session_state['reset_token_email']
                    if not new_password or not confirm_new_password:
                        st.error("New password fields are required.")
                    elif new_password != confirm_new_password:
                        st.error("New passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("New password must be at least 6 characters long.")
                    elif self.user_manager.verify_otp(email, otp_input):
                        hashed_new_password = self.password_utils.hash_password(new_password)
                        if self.user_manager.update_user_password(email, hashed_new_password):
                            st.success("Your password has been reset successfully. You can now log in.")
                            del st.session_state['reset_email_sent']
                            del st.session_state['reset_token_email']
                            st.session_state['auth_page_selection'] = 'Login'
                            st.rerun()
                        else:
                            st.error("Failed to update password. Please try again.")
                    else:
                        st.error("Invalid OTP or OTP expired. Please try again or re-send request.")
