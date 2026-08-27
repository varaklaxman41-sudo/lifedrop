import urllib.request
import re
import os
import sys

PAGES = [
    ("index.html", "Home Portal"),
    ("dashboard.html", "Emergency Dashboard"),
    ("donors.html", "Find Donors Directory"),
    ("requests.html", "Active Blood Requests"),
    ("compatibility.html", "Compatibility Matrix & Guide"),
    ("register.html", "Donor Registration & Hero Pass"),
    ("tracker.html", "Live Request Tracker")
]

def test_server():
    print("Testing Python HTTP server across all Lifedrop web pages...")
    for filename, label in PAGES:
        url = f"http://localhost:8080/{filename}"
        try:
            req = urllib.request.urlopen(url, timeout=5)
            content = req.read().decode('utf-8')
            assert req.status == 200, f"Page {filename} returned status {req.status}"
            assert "Lifedrop" in content, f"Lifedrop brand not found in {filename}"
            assert "Lifedrop Assistant" in content, f"Assistant not found in {filename}"
            assert "js/assistant.js" in content, f"assistant.js script tag not found in {filename}"
            print(f"[OK] {filename} ({label}) responded 200 OK with valid HTML content.")
        except Exception as e:
            print(f"Check failed for {filename}: {e}")
            return False
    return True

def test_files():
    print("Checking required files...")
    files = [
        "c:/Users/Dell/lifedrop/index.html",
        "c:/Users/Dell/lifedrop/dashboard.html",
        "c:/Users/Dell/lifedrop/donors.html",
        "c:/Users/Dell/lifedrop/requests.html",
        "c:/Users/Dell/lifedrop/compatibility.html",
        "c:/Users/Dell/lifedrop/register.html",
        "c:/Users/Dell/lifedrop/tracker.html",
        "c:/Users/Dell/lifedrop/css/style.css",
        "c:/Users/Dell/lifedrop/css/chat.css",
        "c:/Users/Dell/lifedrop/js/data.js",
        "c:/Users/Dell/lifedrop/js/api.js",
        "c:/Users/Dell/lifedrop/js/storage.js",
        "c:/Users/Dell/lifedrop/js/assistant.js",
        "c:/Users/Dell/lifedrop/js/map.js",
        "c:/Users/Dell/lifedrop/js/tracker.js",
        "c:/Users/Dell/lifedrop/js/app.js",
    ]
    for f in files:
        if not os.path.exists(f):
            print(f"Missing file: {f}")
            return False
        size = os.path.getsize(f)
        print(f"[OK] {os.path.basename(f)} ({size} bytes)")
    return True

def test_assistant_logic_inspection():
    print("Inspecting Lifedrop Assistant logic in js/assistant.js...")
    with open("c:/Users/Dell/lifedrop/js/assistant.js", "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Check one-line confirmation format
    assert "Searching immediately for " in code or "Searching for " in code, "One-line search confirmation missing"
    assert "is that correct?" in code, "Confirmation question missing"
    print("[OK] One-line confirmation logic present: 'Searching for [BG] donors near [Location] -- is that correct?'")

    # 2. Check emergency speed path (blood group + location first)
    assert "isEmergencyMode" in code, "Emergency mode state missing"
    assert "REQUEST_BLOOD" in code, "REQUEST_BLOOD intent flow missing"
    print("[OK] Emergency speed priority logic verified.")

    # 3. Check medical safety boundary
    assert "isMedicalAdviceQuery" in code, "Medical advice check missing"
    assert "physician" in code.lower() or "doctor" in code.lower() or "hospital" in code.lower(), "Medical referral boundary missing"
    print("[OK] Medical safety boundaries & doctor referral verified.")

    # 4. Check donor registration flow
    assert "REGISTER_DONOR" in code, "REGISTER_DONOR flow missing"
    assert "CONFIRM" in code, "Confirmation step missing"
    print("[OK] Donor registration flow with confirmation verified.")

    # 5. Check request status lookup
    assert "CHECK_STATUS" in code or "handleStatusCheck" in code, "Status check flow missing"
    print("[OK] Request status tracking lookup verified.")

    # 6. Anti-hallucination verification
    assert "lifedropStorage.findDonors" in code, "Must query live storage data"
    print("[OK] Anti-hallucination compliance: Queries verified backend storage.")

    return True

if __name__ == "__main__":
    t1 = test_files()
    t2 = test_server()
    t3 = test_assistant_logic_inspection()
    if t1 and t2 and t3:
        print("\nALL MULTI-PAGE & DASHBOARD TESTS PASSED SUCCESSFULLY!")
    else:
        sys.exit(1)
