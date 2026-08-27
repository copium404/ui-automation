import re
import time
import uiautomator2 as u2

# ============================================================
# CONFIG
# ============================================================

SERIAL = ""          # ADB serial or IP:PORT
TARGET_USERNAME = "" # Instagram username
TARGET_COUNT = 1      # Number of new Likes

PROFILE_SCROLL_ID = (
    "com.instagram.android:id/"
    "swipeable_nav_view_pager_inner_recycler_view"
)

PROFILE_POST_COUNT_ID = (
    "com.instagram.android:id/"
    "profile_header_post_count_front_familiar"
)

INSTAGRAM_PACKAGE = "com.instagram.android"

SEARCH_TAB_ID = "com.instagram.android:id/search_tab"
SEARCH_INPUT_ID = "com.instagram.android:id/action_bar_search_edit_text"
SEARCH_RESULT_CONTAINER_ID = "com.instagram.android:id/row_search_user_container"
SEARCH_RESULT_USERNAME_ID = "com.instagram.android:id/row_search_user_username"

PROFILE_TITLE_ID = "com.instagram.android:id/action_bar_title"
PROFILE_TAB_ID = "com.instagram.android:id/profile_tab_icon_view"

GRID_POST_ID = "com.instagram.android:id/image_button"
LIKE_BUTTON_ID = "com.instagram.android:id/row_feed_button_like"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_total_profile_posts():
    post_count_element = d(resourceId=PROFILE_POST_COUNT_ID)

    if not post_count_element.exists(timeout=2):
        return None

    info = post_count_element.info

    raw_value = (
        info.get("contentDescription")
        or info.get("text")
        or ""
    )

    match = re.search(r"\d+", raw_value)

    if not match:
        return None

    return int(match.group())


def get_visible_post_data():
    posts = d(resourceId=GRID_POST_ID)
    result = []

    for index in range(posts.count):
        info = posts[index].info
        description = info.get("contentDescription")

        if not description:
            continue

        result.append(
            {
                "description": description,
                "clickable": info.get("clickable"),
                "bounds": info.get("bounds"),
            }
        )

    return result


def open_post_by_description(description):
    post = d(
        resourceId=GRID_POST_ID,
        description=description,
    )

    if not post.exists(timeout=3):
        return False

    post.click()
    return True


def scroll_profile_forward():
    scroller = d(resourceId=PROFILE_SCROLL_ID)

    if not scroller.exists(timeout=5):
        print("FAILED: Profile scroll container not found.")
        return False

    print("Scrolling profile...")

    try:
        scroller.scroll.vert.forward(steps=80)
    except Exception as error:
        print(f"FAILED: Profile scroll error: {error}")
        return False

    time.sleep(1)
    return True


def stop_with_error(message):
    print(f"FAILED: {message}")
    raise SystemExit(1)


def verify_instagram_open():
    current_app = d.app_current()
    print("Current app:", current_app)

    if current_app.get("package") != INSTAGRAM_PACKAGE:
        stop_with_error("Instagram did not open.")


def verify_target_profile():
    profile_title = d(
        resourceId=PROFILE_TITLE_ID,
        text=TARGET_USERNAME,
    )

    if not profile_title.exists(timeout=10):
        stop_with_error(
            "Wrong profile or target profile title was not detected."
        )

    return profile_title


def get_visible_posts():
    return d(resourceId=GRID_POST_ID)


def process_current_post():
    like_button = d(
        resourceId=LIKE_BUTTON_ID,
        description="Like",
    )

    liked_button = d(
        resourceId=LIKE_BUTTON_ID,
        description="Liked",
    )

    state_found = False

    for _ in range(10):
        if (
            like_button.exists(timeout=0)
            or liked_button.exists(timeout=0)
        ):
            state_found = True
            break

        time.sleep(0.5)

    if not state_found:
        print("    FAILED: Like/Liked state not found.")
        return "FAILED"

    if liked_button.exists(timeout=0):
        print("    SKIP: Post already liked.")
        return "SKIP"

    print("    State: Like")
    print("    Clicking clickable Like parent...")

    like_parent_xpath = (
        f'//*[@resource-id="{LIKE_BUTTON_ID}" '
        f'and @content-desc="Like"]/..'
    )

    like_parent = d.xpath(like_parent_xpath)

    if not like_parent.wait(timeout=5):
        print("    FAILED: Clickable Like parent not found.")
        return "FAILED"

    like_parent.click()

    if liked_button.exists(timeout=5):
        print("    SUCCESS: Like -> Liked.")
        return "SUCCESS"

    print("    FAILED: Liked state not detected after click.")
    return "FAILED"


# ============================================================
# CONNECT DEVICE
# ============================================================

print("Connecting to device...")
d = u2.connect(SERIAL)
print("Device connected.")


# ============================================================
# STEP 1 - OPEN INSTAGRAM
# ============================================================

print("\n[1] Opening Instagram...")
d.app_start(INSTAGRAM_PACKAGE)
time.sleep(2)

verify_instagram_open()
print("SUCCESS: Instagram opened.")


# ============================================================
# STEP 2 - OPEN SEARCH
# ============================================================

print("\n[2] Opening Search...")
search_tab = d(resourceId=SEARCH_TAB_ID)

if not search_tab.exists(timeout=10):
    stop_with_error("Search tab not found.")

search_tab.click()
print("SUCCESS: Search tab clicked.")


# ============================================================
# STEP 3 - FIND SEARCH INPUT
# ============================================================

print("\n[3] Looking for search input...")
search_input = d(resourceId=SEARCH_INPUT_ID)

if not search_input.exists(timeout=10):
    stop_with_error("Search input not found.")

print("SUCCESS: Search input found.")


# ============================================================
# STEP 4 - TYPE TARGET USERNAME
# ============================================================

print(f"\n[4] Searching username: {TARGET_USERNAME}")

search_input.click()
search_input.clear_text()
search_input.set_text(TARGET_USERNAME)

time.sleep(2)
print("SUCCESS: Username entered.")


# ============================================================
# STEP 5 - FIND EXACT SEARCH RESULT
# ============================================================

print("\n[5] Looking for exact search result...")

result_xpath = (
    f'//*[@resource-id="{SEARCH_RESULT_CONTAINER_ID}"]'
    f'[.//*[@resource-id="{SEARCH_RESULT_USERNAME_ID}" '
    f'and @text="{TARGET_USERNAME}"]]'
)

search_result = d.xpath(result_xpath)

if not search_result.wait(timeout=10):
    stop_with_error(
        f'Exact username "{TARGET_USERNAME}" was not found.'
    )

print(f"SUCCESS: Exact result found: {TARGET_USERNAME}")


# ============================================================
# STEP 6 - OPEN TARGET PROFILE
# ============================================================

print("\n[6] Opening target profile...")
search_result.click()

time.sleep(2)
print("SUCCESS: Target profile opened.")


# ============================================================
# STEP 7 - VERIFY TARGET PROFILE
# ============================================================

print("\n[7] Verifying target profile...")
profile_title = verify_target_profile()

print("====================================")
print("PROFILE VERIFICATION SUCCESS")
print("====================================")
print("Target username :", TARGET_USERNAME)
print("Current profile :", profile_title.get_text())
print("Status          : MATCH")
print("====================================")


# ============================================================
# STEP 8 - OPEN GRID VIEW
# ============================================================

print("\n[8] Opening profile grid...")

grid_tab = d(
    resourceId=PROFILE_TAB_ID,
    description="Grid view",
)

if not grid_tab.exists(timeout=10):
    stop_with_error("Grid view tab not found.")

grid_tab.click()
time.sleep(1)

print("SUCCESS: Grid view opened.")


# ============================================================
# STEP 9 - READ PROFILE INFORMATION
# ============================================================

print("\n[9] Reading profile information...")

total_profile_posts = get_total_profile_posts()

if total_profile_posts is not None:
    print(f"Total profile posts : {total_profile_posts}")
else:
    print("Total profile posts : Unknown")

print(f"Requested new Likes : {TARGET_COUNT}")


# ============================================================
# STEP 10 - PROCESS POSTS WITH SCROLLING
# ============================================================

print("\n====================================")
print("PROCESSING PROFILE POSTS")
print("====================================")

success_count = 0
skipped_count = 0
failed_count = 0

processed_posts = set()

scroll_count = 0
max_scrolls = 20

no_new_post_rounds = 0
max_no_new_post_rounds = 2


while success_count < TARGET_COUNT:

    print("\n------------------------------------")
    print(f"Progress: {success_count}/{TARGET_COUNT} new Likes")
    print("------------------------------------")

    visible_posts = get_visible_post_data()

    print(f"Visible grid posts: {len(visible_posts)}")

    new_posts = [
        post
        for post in visible_posts
        if post["description"] not in processed_posts
    ]

    print(f"New unprocessed posts: {len(new_posts)}")

    for post_data in new_posts:

        if success_count >= TARGET_COUNT:
            break

        description = post_data["description"]

        print("\nProcessing:")
        print(f"    {description}")

        processed_posts.add(description)

        if not open_post_by_description(description):
            print("    FAILED: Could not open post.")
            failed_count += 1
            continue

        time.sleep(1.5)

        result = process_current_post()

        if result == "SUCCESS":
            success_count += 1
        elif result == "SKIP":
            skipped_count += 1
        else:
            failed_count += 1

        print(f"    Progress: {success_count}/{TARGET_COUNT}")
        print("    Returning to target profile...")

        d.press("back")
        time.sleep(1)

        verify_target_profile()
        print("    Profile verified.")

    if success_count >= TARGET_COUNT:
        print("\nTarget Like count reached.")
        break

    if (
        total_profile_posts is not None
        and len(processed_posts) >= total_profile_posts
    ):
        print(
            "\nAll available profile posts "
            "have been inspected."
        )
        break

    if scroll_count >= max_scrolls:
        print("\nMaximum scroll limit reached.")
        break

    before_scroll = {
        post["description"]
        for post in visible_posts
    }

    if not scroll_profile_forward():
        break

    scroll_count += 1

    after_scroll_posts = get_visible_post_data()

    after_scroll = {
        post["description"]
        for post in after_scroll_posts
    }

    newly_visible = after_scroll - before_scroll

    if newly_visible:
        no_new_post_rounds = 0
        print(f"New posts after scroll: {len(newly_visible)}")
    else:
        no_new_post_rounds += 1
        print("No new grid posts detected after scroll.")

        if no_new_post_rounds >= max_no_new_post_rounds:
            print(
                "Reached end of profile "
                "or no additional posts are available."
            )
            break


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n====================================")
print("WORKFLOW COMPLETED")
print("====================================")
print("Target username :", TARGET_USERNAME)

if total_profile_posts is not None:
    print("Profile posts   :", total_profile_posts)

print("Requested Likes :", TARGET_COUNT)
print("New Likes       :", success_count)
print("Already Liked   :", skipped_count)
print("Failed          :", failed_count)
print("Posts inspected :", len(processed_posts))
print("Scrolls         :", scroll_count)

if success_count >= TARGET_COUNT:
    print("Result          : TARGET COMPLETED")
else:
    print("Result          : PARTIAL")

print("====================================")
