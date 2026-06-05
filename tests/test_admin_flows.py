import re
from playwright.sync_api import Page, expect
from conftest import BASE_URL


def login_as_admin(page: Page):
    """Helper to login as Admin before tests."""
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("input[type='email']", state="visible")
    page.get_by_placeholder("Enter email").fill("admin@lms.com", force=True)
    page.get_by_placeholder("Password").fill("admin123", force=True)
    page.get_by_role("button", name="SIGN IN", exact=False).click()
    # React SPA uses client-side routing — wait for URL change instead of navigation event
    page.wait_for_url("**/admin-dashboard**", timeout=15000)
    expect(page).to_have_url(re.compile(r".*/admin-dashboard"), timeout=15000)

def test_admin_dashboard_renders(page: Page):
    """Test if Admin Dashboard renders primary components after login."""
    login_as_admin(page)
    # Wait for dashboard to load
    page.wait_for_selector("text=Total Courses", state="visible")
    expect(page.get_by_role("link", name=re.compile("Users", re.IGNORECASE))).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("Courses", re.IGNORECASE))).to_be_visible()

def test_admin_navigate_to_manage_users(page: Page):
    """Test navigation from admin dashboard to User management."""
    login_as_admin(page)
    
    # Click link or button to manage users
    # Adjust `name` appropriately if labeled "Manage Users" vs "Users"
    manage_link = page.get_by_role("link", name=re.compile("manage.*user|user", re.IGNORECASE)).first
    if manage_link:
        manage_link.click()
    else:
        page.goto(f"{BASE_URL}/admin-dashboard/users") # fallback direct navigation

    # Assume table or heading exists
    expect(page.get_by_role("heading", name=re.compile("user", re.IGNORECASE))).to_be_visible()

def test_admin_navigate_to_manage_courses(page: Page):
    """Test navigation to Courses management."""
    login_as_admin(page)
    
    # Click link to manage courses
    course_link = page.get_by_role("link", name=re.compile("manage.*course|course", re.IGNORECASE)).first
    if course_link:
        course_link.click()
    else:
        page.goto(f"{BASE_URL}/admin-dashboard/courses")
        
    expect(page.get_by_role("heading", name=re.compile("course", re.IGNORECASE))).to_be_visible()
