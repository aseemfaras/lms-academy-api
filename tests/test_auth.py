import re
import pytest
from playwright.sync_api import Page, expect
from conftest import BASE_URL


def test_successful_admin_login(page: Page):
    """Admin login flow test."""
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    # Wait explicitly for the input to hit the DOM
    page.wait_for_selector("input[type='email']", state="visible")
    page.get_by_placeholder("Enter email").fill("admin@lms.com", force=True)
    page.get_by_placeholder("Password").fill("admin123", force=True)
    page.get_by_role("button", name="SIGN IN", exact=False).click()
    # React SPA uses client-side routing — wait for URL change instead of navigation event
    page.wait_for_url("**/admin-dashboard**", timeout=15000)

    # Assert successful redirect to Admin Dashboard
    expect(page).to_have_url(re.compile(r".*/admin-dashboard"), timeout=15000)
    # Verify protected route guard successfully authorized the admin
    expect(page.get_by_role("navigation")).to_be_visible(timeout=10000)

def test_successful_trainer_login(page: Page):
    """Trainer login flow test."""
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("input[type='email']", state="visible")
    page.get_by_placeholder("Enter email").fill("trainer@lms.com", force=True)
    page.get_by_placeholder("Password").fill("trainer123", force=True)
    page.get_by_role("button", name="SIGN IN", exact=False).click()
    # React SPA uses client-side routing — wait for URL change instead of navigation event
    page.wait_for_url("**/trainer-dashboard**", timeout=15000)

    # Assert successful redirect to Trainer Dashboard
    expect(page).to_have_url(re.compile(r".*/trainer-dashboard"), timeout=15000)
    expect(page.get_by_role("navigation")).to_be_visible(timeout=10000)

def test_successful_student_login(page: Page):
    """Student login flow test."""
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("input[type='email']", state="visible")
    page.get_by_placeholder("Enter email").fill("anithakommoji78@gmail.com", force=True)
    page.get_by_placeholder("Password").fill("password123", force=True)
    page.get_by_role("button", name="SIGN IN", exact=False).click()
    # React SPA uses client-side routing — wait for URL change instead of navigation event
    page.wait_for_url("**/dashboard**", timeout=15000)

    # Assert successful redirect to Student Dashboard
    expect(page).to_have_url(re.compile(r".*/dashboard"), timeout=15000)
    expect(page.get_by_role("navigation")).to_be_visible(timeout=10000)

def test_invalid_credentials(page: Page):
    """Test login failure flow."""
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("input[type='email']", state="visible")
    page.get_by_placeholder("Enter email").fill("wrong@user.com", force=True)
    page.get_by_placeholder("Password").fill("wrongpassword", force=True)
    page.get_by_role("button", name="SIGN IN", exact=False).click()
    
    # Expect URL to remain on login
    expect(page).to_have_url(re.compile(r".*/login"))
    
def test_protected_route_guard_redirect(page: Page):
    """Test unauthenticated access is blocked and redirected to login."""
    # Try accessing a protected admin route directly without logging in
    page.goto(f"{BASE_URL}/admin-dashboard")
    
    # Expect redirection back to login
    expect(page).to_have_url(re.compile(r".*/login"))
