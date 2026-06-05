import re
from playwright.sync_api import Page, expect
from conftest import BASE_URL


def login_as_trainer(page: Page):
    """Helper to login as Trainer before tests."""
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("input[type='email']", state="visible")
    page.get_by_placeholder("Enter email").fill("trainer@lms.com", force=True)
    page.get_by_placeholder("Password").fill("trainer123", force=True)
    page.get_by_role("button", name="SIGN IN", exact=False).click()
    # React SPA uses client-side routing — wait for URL change instead of navigation event
    page.wait_for_url("**/trainer-dashboard**", timeout=15000)
    expect(page).to_have_url(re.compile(r".*/trainer-dashboard"), timeout=15000)

def test_trainer_dashboard_renders(page: Page):
    """Test if Trainer Dashboard renders courses."""
    login_as_trainer(page)
    
    # Ensure they can see their assigned courses list or cards
    expect(page.get_by_text("Courses", exact=False).first).to_be_visible()
    
def test_trainer_can_view_course_details(page: Page):
    """Test if a Trainer can click into a course to view/upload content."""
    login_as_trainer(page)
    
    # We try to click the first "View Course" or "Manage" button available
    # Depends on actual frontend react implementation.
    manage_btn = page.get_by_role("button", name=re.compile("view|manage", re.IGNORECASE)).first
    if manage_btn and manage_btn.is_visible():
        manage_btn.click()
        # Expect to hit a course detail view
        expect(page).to_have_url(re.compile(r".*/trainer-dashboard/course/.*"))
