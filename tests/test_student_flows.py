import re
from playwright.sync_api import Page, expect
from conftest import BASE_URL


def login_as_student(page: Page):
    """Helper to login as Student before tests."""
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("input[type='email']", state="visible")
    page.get_by_placeholder("Enter email").fill("anithakommoji78@gmail.com", force=True)
    page.get_by_placeholder("Password").fill("password123", force=True)
    page.get_by_role("button", name="SIGN IN", exact=False).click()
    # React SPA uses client-side routing — wait for URL change instead of navigation event
    page.wait_for_url("**/dashboard**", timeout=15000)
    expect(page).to_have_url(re.compile(r".*/dashboard"), timeout=15000)

def test_student_dashboard_renders(page: Page):
    """Test if Student Dashboard loads and displays components."""
    login_as_student(page)
    
    # Wait for loading to finish and Dashboard elements to render
    page.wait_for_selector("text=My Courses", state="visible")
    expect(page.get_by_role("navigation")).to_be_visible()
    expect(page.get_by_text("My Courses", exact=False)).to_be_visible()
    
def test_student_can_navigate_to_all_courses(page: Page):
    """Test navigation from dashboard to the global courses directory."""
    login_as_student(page)
    
    course_link = page.get_by_role("link", name=re.compile("course", re.IGNORECASE)).first
    if course_link:
        course_link.click()
    else:
        page.goto(f"{BASE_URL}/courses")
        
    # Wait for content to load
    page.wait_for_selector("text=Learning Platform", state="visible")
    expect(page).to_have_url(re.compile(r".*/courses"))
    expect(page.get_by_role("heading", name=re.compile(r"Learning Platform", re.IGNORECASE))).to_be_visible()
