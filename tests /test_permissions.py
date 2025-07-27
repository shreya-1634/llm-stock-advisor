# your_project/tests/test_permissions.py

import pytest

# Adjust imports based on your exact project structure
from auths.permissions import Permissions

# --- Test Cases ---

def test_guest_permissions():
    """Test permissions for a 'guest' role."""
    assert not Permissions.check_permission("guest", "view_charts_basic")
    assert not Permissions.check_permission("guest", "get_predictions")
    assert not Permissions.check_permission("guest", "non_existent_feature")

def test_free_user_permissions():
    """Test permissions for a 'free' user role."""
    assert Permissions.check_permission("free", "view_charts_basic")
    assert Permissions.check_permission("free", "view_news_headlines")
    assert not Permissions.check_permission("free", "get_predictions")
    assert not Permissions.check_permission("free", "view_charts_advanced")

def test_premium_user_permissions():
    """Test permissions for a 'premium' user role."""
    assert Permissions.check_permission("premium", "view_charts_basic")
    assert Permissions.check_permission("premium", "view_charts_advanced")
    assert Permissions.check_permission("premium", "view_news_headlines")
    assert Permissions.check_permission("premium", "view_news_sentiment")
    assert Permissions.check_permission("premium", "get_predictions")
    assert Permissions.check_permission("premium", "get_recommendations")
    assert Permissions.check_permission("premium", "view_volatility")
    assert not Permissions.check_permission("premium", "manage_users") # Assuming admin only

def test_admin_user_permissions():
    """Test permissions for an 'admin' user role (assuming it has all)."""
    assert Permissions.check_permission("admin", "view_charts_basic")
    assert Permissions.check_permission("admin", "get_recommendations")
    assert Permissions.check_permission("admin", "manage_users") # Assuming admin specific
    assert Permissions.check_permission("admin", "any_feature_should_pass") # Admins should have all

def test_unknown_role():
    """Test behavior for an unknown role."""
    assert not Permissions.check_permission("unknown_role", "view_charts_basic")
    assert not Permissions.check_permission("non_existent", "get_predictions")

def test_no_permission_for_valid_role_and_invalid_feature():
    """Test a valid role trying to access an invalid/non-existent feature."""
    assert not Permissions.check_permission("free", "non_existent_feature")
    assert not Permissions.check_permission("premium", "another_non_existent_feature")
