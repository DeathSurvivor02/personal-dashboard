"""
sync_school.py
Auto-sync engine for Ean Bynoe's Personal Workspace & Academic Dashboard.
1. Fetches eCentennial (Brightspace / Luminate) .ics calendar feed (when configured),
   updates assignment due dates in academic_state.json, and builds calendarEvents
   for both assessments and class/lab sessions.
2. Fetches Brightspace/course RSS or Atom announcement feeds (when configured)
   and merges teacher announcements into academic_state.json["announcements"].
3. Scans local Semester 5 workspace folders and Downloads for packaged submission artifacts
   and attaches readiness badges to matching coursework items.
4. Fetches GitHub API telemetry, Chess.com Daily Puzzle & player stats, and Daily Wordle
   target word (with offline fallback) into academic_state.json.
Uses Python standard library only.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "school_sync_config.json")
STATE_PATH = os.path.join(BASE_DIR, "academic_state.json")

WORDLE_FALLBACK_BANK = [
    "CRANE", "SLATE", "AUDIO", "STARE", "TRACE", "ROAST", "RAISE", "ARISE", "IRATE", "STERN",
    "PLAIN", "BRAVE", "CHIME", "DWELL", "EMBER", "FLAME", "GLIDE", "HEART", "INDEX", "JOUST",
    "KNIGHT", "LOGIC", "MOUNT", "NERVE", "ORBIT", "PRISM", "QUERY", "RUSTY", "SCALE", "TOKEN",
    "UNITY", "VALID", "WATCH", "YIELD", "ZESTY", "ARRAY", "ASYNC", "BYTES", "CACHE", "CLOUD",
    "CODEC", "DELTA", "EPOCH", "FETCH", "FLOAT", "GRAPH", "GUARD", "INPUT", "LAYER", "LINUX",
    "MACRO", "MERGE", "MUTEX", "NODES", "OAUTH", "PARSE", "PATCH", "PIXEL", "PROXY", "QUEUE",
    "REACT", "ROUTE", "SCOPE", "SHARD", "SHELL", "SHIFT", "SLICE", "SOLVE", "STACK", "STATE",
    "STORE", "STYLE", "SWIFT", "TABLE", "TESTS", "THEME", "TIMER", "TRAIT", "TUPLE", "TYPES",
    "VALUE", "VAULT", "WHILE", "WIDTH", "WRITE", "ACTOR", "AGENT", "ALERT", "ALIGN", "ALPHA",
    "ANGEL", "ANGLE", "ANKLE", "APPLE", "ARROW", "BASIC", "BEACH", "BENCH", "BLEND", "BLOCK",
    "BOARD", "BOOST", "BOUND", "BRAIN", "BREAD", "BRICK", "BRIEF", "BRING", "BUILD", "BUILT",
    "CABLE", "CHARM", "CHART", "CHECK", "CHESS", "CLEAN", "CLEAR", "CLICK", "CLOCK", "CLOSE",
]
WORDLE_FALLBACK_BANK = [w for w in WORDLE_FALLBACK_BANK if len(w) == 5]

KNOWN_COURSES = {
    "COMP303": "comp303",
    "COMP309": "comp309",
    "COMP231": "comp231",
    "COMP307": "comp307",
    "COMP255": "comp255",
    "COMP306": "comp306",
}

LUMINATE_BASE = "https://luminate.centennialcollege.ca"
LUMINATE_COURSE_IDS = {
    "comp303": "_42886_1",
    "comp309": "_43994_1",
    "comp231": "_43982_1",
    "comp307": "_46514_1",
    "comp255": "_43483_1",
    "comp306": "_45231_1",
}

SUBMISSION_URLS = {
    "comp303::Assignment 3: Spring Boot REST App": f"{LUMINATE_BASE}/ultra/courses/_42886_1/assessment/_6105756_1/overview?courseId=_42886_1",
    "comp309::COMP 309 Analytics Project (10%)": f"{LUMINATE_BASE}/ultra/courses/_43994_1/assessment/_6112492_1/overview?courseId=_43994_1",
    "comp309::Bonus Activity": f"{LUMINATE_BASE}/ultra/course/assessment/_6315878_1/open?courseId=_43994_1",
    "comp307::Lab Assignment 6 (LFI/RFI)": f"{LUMINATE_BASE}/ultra/courses/_46514_1/assessment/_5804531_1/overview?courseId=_46514_1",
    "comp307::Research Project Submission": f"{LUMINATE_BASE}/ultra/courses/_46514_1/assessment/_5804511_1/overview?courseId=_46514_1",
    "comp307::Discussions #4 (Week 10)": f"{LUMINATE_BASE}/ultra/courses/_46514_1/discussion/_5804424_1?view=discussions",
    "comp231::Progress Monitoring (Iteration 1)": f"{LUMINATE_BASE}/ultra/courses/_43982_1/assessment/_5672104_1/overview?courseId=_43982_1",
    "comp231::Iteration 2 Planning": f"{LUMINATE_BASE}/ultra/courses/_43982_1/assessment/_5672105_1/overview?courseId=_43982_1",
    "comp231::Progress Monitoring (Iteration 2)": f"{LUMINATE_BASE}/ultra/courses/_43982_1/assessment/_5672106_1/overview?courseId=_43982_1",
    "comp231::Software Release 1.0": f"{LUMINATE_BASE}/ultra/courses/_43982_1/assessment/_5672107_1/overview?courseId=_43982_1",
    "comp306::Project Proposal": f"{LUMINATE_BASE}/ultra/courses/_45231_1/assessment/_6172047_1/overview?courseId=_45231_1",
    "comp306::Cloud Engineering Project: Implementation": f"{LUMINATE_BASE}/ultra/courses/_45231_1/assessment/_6172048_1/overview?courseId=_45231_1",
}

# Maps Luminate GradableItem IDs (from learn.ics UIDs) to courseId & baseline item titles
GRADABLE_ITEM_MAP = {
    # COMP303
    "_676029_1": ("comp303", "Assignment 3: Spring Boot REST App"),
    # COMP309
    "_676642_1": ("comp309", "COMP 309 Analytics Project (10%)"),
    "_695494_1": ("comp309", "Bonus Activity"),
    # COMP231
    "_638449_1": ("comp231", "Progress Monitoring (Iteration 1)"),
    "_638450_1": ("comp231", "Iteration 2 Planning"),
    "_638451_1": ("comp231", "Progress Monitoring (Iteration 2)"),
    "_638452_1": ("comp231", "Software Release 1.0"),
    "_638453_1": ("comp231", "TAC Technical Report"),
    "_638454_1": ("comp231", "Peer Evaluation"),
    # COMP307
    "_652385_1": ("comp307", "Lab Assignment 5"),
    "_652386_1": ("comp307", "Lab Assignment 6 (LFI/RFI)"),
    "_652390_1": ("comp307", "Research Project Submission"),
    "_652380_1": ("comp307", "Discussions #4 (Week 10)"),
    # COMP306
    "_681667_1": ("comp306", "Lab 3: Full-Stack Cloud App"),
    "_681668_1": ("comp306", "Project Proposal"),
    "_681669_1": ("comp306", "Cloud Engineering Project: Implementation"),
    "_681671_1": ("comp306", "Presentation & Report"),
}

BASELINE_ITEM_TITLES = {
    "comp303": [
        "Assignment 3: Spring Boot REST App",
        "Term Project: Final Deliverables & Code",
        "Final Test 3 (Practical Exam)",
    ],
    "comp231": [
        "Progress Monitoring (Iteration 1)",
        "Iteration 2 Planning",
        "Progress Monitoring (Iteration 2)",
        "Software Release 1.0",
        "TAC Technical Report",
        "Peer Evaluation",
    ],
    "comp309": [
        "COMP 309 Analytics Project (10%)",
        "Bonus Activity",
        "Quiz 2 (Post-Midterm)",
        "Final Examination",
    ],
    "comp307": [
        "Lab Assignment 5",
        "Lab Assignment 6 (LFI/RFI)",
        "Research Project Submission",
        "Discussions #4 (Week 10)",
    ],
    "comp255": [
        "Assignment #1 - Lean Canvas",
        "Quizzes #2-#8 & Weekly Discussions (Weeks 1-11)",
        "Final Examination",
    ],
    "comp306": [
        "Project Proposal",
        "Lab 3: Full-Stack Cloud App",
        "Cloud Engineering Project: Implementation",
        "Presentation & Report",
    ],
}

# Verified Centennial Luminate Announcements & Discussions per course
LUMINATE_COURSE_FEED = [
    {
        "id": "lum_comp303_a3_demo",
        "course": "COMP303",
        "kind": "Teacher Announcement",
        "title": "Assignment 3 Due & Lab Demo (In-Person or 10-15 Min Video)",
        "body": "Assignment 3 is due Tue Nov 17 by 11:59 PM in Gradebook -> Assignment 3. Demo in Lab A1-22 on Wed Nov 18 at 12:30 PM (both pair members present) OR upload a 10-15 min webcam-intro demo video individually.",
        "timestamp": "2026-11-17 21:00",
        "source": "Luminate (Dr. Vinay)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_42886_1/assessment/_6105756_1/overview?courseId=_42886_1",
        "urgent": True,
        "pinned": True,
    },
    {
        "id": "lum_comp303_final_group",
        "course": "COMP303",
        "kind": "Teacher Announcement",
        "title": "Join a Group for COMP303 Final Group Project",
        "body": "Reminder to enroll in a project group on Luminate before the enrollment deadline for the Final Group Project.",
        "timestamp": "2026-11-11 00:00",
        "source": "Luminate (Dr. Vinay)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_42886_1/groups/enrollments",
        "urgent": False,
        "pinned": False,
    },
    {
        "id": "lum_comp309_analytics_checkpoint",
        "course": "COMP309",
        "kind": "Teacher Announcement",
        "title": "Analytics Project (10%) Draft Saved — Due Nov 18 @ 8:30 AM",
        "body": "COMP 309 Analytics project (10%) is in Draft saved state for New Group 8 (due 11/18/26, 8:30 AM EST). Upload COMP309_Vehicle_Theft_Project.zip and finalize submission.",
        "timestamp": "2026-11-17 10:30",
        "source": "Luminate (Prof. Vijayalakshmi)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_43994_1/assessment/_6112492_1/overview?courseId=_43994_1",
        "urgent": True,
        "pinned": True,
    },
    {
        "id": "lum_comp309_quiz2",
        "course": "COMP309",
        "kind": "Teacher Announcement",
        "title": "Quiz 2 Reminder — Scheduled Nov 24",
        "body": "Prof. Viji confirmed Quiz 2 will be conducted on Nov 24 covering post-midterm material (and Lab exercise #5 BI was recently graded).",
        "timestamp": "2026-11-11 08:37",
        "source": "Luminate (Prof. Vijayalakshmi)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_43994_1/announcements",
        "urgent": True,
        "pinned": False,
    },
    {
        "id": "lum_comp309_disc_research",
        "course": "COMP309",
        "kind": "Discussion Thread",
        "title": "Research Group Topic Discussion (1 Unread)",
        "body": "Active COMP309 discussion thread for Research Group Topic coordination.",
        "timestamp": "Luminate Discussions",
        "source": "Luminate Discussions",
        "url": f"{LUMINATE_BASE}/ultra/courses/_43994_1/discussion/_6112385_1?view=discussions",
        "urgent": False,
        "pinned": False,
    },
    {
        "id": "lum_comp306_proposal_grade",
        "course": "COMP306",
        "kind": "Teacher Announcement",
        "title": "Project Proposal Graded (6/10) & API Domain Revision Feedback",
        "body": "Standing C+ on Luminate (Attendance 66.66%, Midterm 27/50, Lab 1 17.5/20, Lab 2 19/25, Proposal 6/10). Prof. Yin Hua Li advised revising the RESTful API domain per Clarification-GroupProjectProposal.docx before Implementation (Nov 27).",
        "timestamp": "2026-11-14",
        "source": "Luminate (Yin Hua Li)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_45231_1/assessment/_6172047_1/overview?courseId=_45231_1",
        "urgent": True,
        "pinned": True,
    },
    {
        "id": "lum_comp306_lab3_notes",
        "course": "COMP306",
        "kind": "Teacher Announcement",
        "title": "Lab #3 Submission Criteria & Grading Deductions",
        "body": "Show persistence in both Amazon RDS & DynamoDB (-4 if omitted), increment view count on item detail open (-0.5), and filter most popular by highest views (-1).",
        "timestamp": "2026-11-06 15:15",
        "source": "Luminate (Yin Hua Li)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_45231_1/announcements",
        "urgent": False,
        "pinned": False,
    },
    {
        "id": "lum_comp306_disc_general",
        "course": "COMP306",
        "kind": "Discussion Thread",
        "title": "General Discussion Forum: Introductions & Comments/Questions",
        "body": "Two open discussion threads in COMP306 under General Discussion Forum.",
        "timestamp": "Luminate Discussions",
        "source": "Luminate Discussions",
        "url": f"{LUMINATE_BASE}/ultra/courses/_45231_1/engagement",
        "urgent": False,
        "pinned": False,
    },
    {
        "id": "lum_comp307_disc4",
        "course": "COMP307",
        "kind": "Discussion Due",
        "title": "Discussion Board 4 (Week 10) Due Nov 25 — Pair Post + Peer Reply",
        "body": "Standing 74.32%. Task 1: pick 1 PCI-DSS v4.0 principle & best practice; Task 2: Website Deployment Checklist examples. Include both pair names + reply to 1 peer by 11/25/26 11:59 PM EST.",
        "timestamp": "Due Nov 25 - 23:59",
        "source": "Luminate (Bindu Goel)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_46514_1/discussion/_5804424_1?view=discussions",
        "urgent": True,
        "pinned": True,
    },
    {
        "id": "lum_comp307_ebook",
        "course": "COMP307",
        "kind": "Teacher Announcement",
        "title": "Course e-Book Access Links (EBSCO / Safari / ProQuest)",
        "body": "Prof. Bindu Goel posted Centennial Library, EBSCO, Safari Books, and ProQuest direct links for the Software Security textbook.",
        "timestamp": "2026-11-02 06:18",
        "source": "Luminate (Bindu Goel)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_46514_1/announcements",
        "urgent": False,
        "pinned": False,
    },
    {
        "id": "lum_comp231_disc",
        "course": "COMP231",
        "kind": "Discussion Thread",
        "title": "Group Project Discussion Area & Progress Monitoring (Nov 22)",
        "body": "Standing A (User Role Modelling 100%, Proposal 100%, Release Plan 90%, Iteration 1 Planning 90%). Progress Monitoring (Iteration 1) is in Draft saved state for Nov 22.",
        "timestamp": "Due Nov 22 - 23:59",
        "source": "Luminate (Jin Li)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_43982_1/assessment/_5672104_1/overview?courseId=_43982_1",
        "urgent": False,
        "pinned": False,
    },
    {
        "id": "lum_comp255_schedule",
        "course": "COMP255",
        "kind": "Discussion Thread",
        "title": "Modules 10-13 Schedule, Lean Canvas Draft & Discussion Questions",
        "body": "Standing B+ (Quiz #1 8/11, Mid-Term 80%). Assignment #1 Lean Canvas is Draft saved; Week 1-11 discussion forums (31 unread) & Quizzes #2-#8 due by Dec 18.",
        "timestamp": "Schedule / Dec 18",
        "source": "Luminate (Jean-Luc David)",
        "url": f"{LUMINATE_BASE}/ultra/courses/_43483_1/engagement",
        "urgent": False,
        "pinned": False,
    },
]


def load_json(path, default):
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def unfold_ics_lines(raw_text):
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"\n[ \t]", "", normalized).split("\n")


def unescape_ics_text(val):
    return (
        val.replace("\\n", " ")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
        .strip()
    )


def strip_html(text):
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", cleaned).strip()


def parse_ics_datetime(raw_val):
    cleaned = raw_val.strip()
    m = re.match(r"^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})(Z)?)?$", cleaned)
    if not m:
        return None
    yr, mo, dy = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hr = int(m.group(4) or 23)
    mn = int(m.group(5) or 59)
    sc = int(m.group(6) or 0)
    is_utc = m.group(7) == "Z"

    if is_utc:
        dt_utc = datetime(yr, mo, dy, hr, mn, sc, tzinfo=timezone.utc)
        dt_local = dt_utc.astimezone()
    else:
        dt_local = datetime(yr, mo, dy, hr, mn, sc)

    due_iso = dt_local.strftime("%Y-%m-%dT%H:%M:%S")
    due_label = dt_local.strftime("%b %d - %H:%M")
    return due_iso, due_label


def parse_ics_events(raw_text):
    events = []
    cur = None
    for line in unfold_ics_lines(raw_text):
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT":
            if cur and cur.get("SUMMARY"):
                events.append(cur)
            cur = None
        elif cur is not None and ":" in line:
            key_part, val = line.split(":", 1)
            prop_name = key_part.split(";", 1)[0].upper()
            cur[prop_name] = unescape_ics_text(val)
    return events


def parse_rss_announcements(raw_xml, source_label="Course RSS"):
    items = []
    root = ET.fromstring(raw_xml)

    # Support RSS 2.0 (<channel>/<item>)
    for item in root.findall(".//item"):
        title = strip_html(item.findtext("title") or "")
        desc = strip_html(item.findtext("description") or "")
        pub = (item.findtext("pubDate") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link or title).strip()
        if not title:
            continue
        code = detect_course_id(f"{title} {desc} {source_label}") or "general"
        ann_id = "rss_" + hashlib.sha1(guid.encode("utf-8")).hexdigest()[:12]
        items.append({
            "id": ann_id,
            "course": code.upper() if code != "general" else "GENERAL",
            "kind": "Teacher Announcement",
            "title": title,
            "body": desc[:320] if desc else "Posted via course announcement feed.",
            "timestamp": pub or datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source": source_label,
            "urgent": any(w in (title + " " + desc).lower() for w in ["urgent", "deadline", "cancelled", "canceled", "moved", "quiz", "exam", "due"]),
            "pinned": False,
            "read": False,
        })

    # Support Atom (<entry>)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", ns) + root.findall(".//entry"):
        title = strip_html(entry.findtext("atom:title", default="", namespaces=ns) or entry.findtext("title") or "")
        body = strip_html(
            entry.findtext("atom:summary", default="", namespaces=ns)
            or entry.findtext("atom:content", default="", namespaces=ns)
            or entry.findtext("summary")
            or entry.findtext("content")
            or ""
        )
        updated = (entry.findtext("atom:updated", default="", namespaces=ns) or entry.findtext("updated") or "").strip()
        eid = (entry.findtext("atom:id", default="", namespaces=ns) or entry.findtext("id") or title).strip()
        if not title:
            continue
        code = detect_course_id(f"{title} {body} {source_label}") or "general"
        ann_id = "rss_" + hashlib.sha1(eid.encode("utf-8")).hexdigest()[:12]
        items.append({
            "id": ann_id,
            "course": code.upper() if code != "general" else "GENERAL",
            "kind": "Teacher Announcement",
            "title": title,
            "body": body[:320] if body else "Posted via course announcement feed.",
            "timestamp": updated or datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source": source_label,
            "urgent": any(w in (title + " " + body).lower() for w in ["urgent", "deadline", "cancelled", "canceled", "moved", "quiz", "exam", "due"]),
            "pinned": False,
            "read": False,
        })
    return items


def detect_course_id(text_blob):
    upper = text_blob.upper()
    m = re.search(r"\bCOMP[\s\-_]?(\d{3})\b", upper)
    if m:
        code = f"COMP{m.group(1)}"
        if code in KNOWN_COURSES:
            return KNOWN_COURSES[code]
    return None


def resolve_gradable_item(uid, summary):
    m = re.search(r"GradableItem-(_\d+_\d+)", uid or "")
    if m and m.group(1) in GRADABLE_ITEM_MAP:
        return GRADABLE_ITEM_MAP[m.group(1)]
    return None, None


def is_lecture_calendar_event(uid, summary):
    if "_blackboard.data.calendar.CalendarEntry-" in (uid or ""):
        return True
    if re.search(r"\(SEC\.\s*\d+\)", summary or "", re.IGNORECASE):
        return True
    return False


def course_grades_url(course_id):
    cid = LUMINATE_COURSE_IDS.get(course_id)
    if cid:
        return f"{LUMINATE_BASE}/ultra/courses/{cid}/grades"
    return f"{LUMINATE_BASE}/ultra/course"


def match_baseline_title(course_id, summary):
    s_low = summary.lower()
    s_tokens = set(re.findall(r"[a-z0-9]+", s_low))
    best_title = None
    best_score = 0
    for title in BASELINE_ITEM_TITLES.get(course_id, []):
        t_tokens = {tok for tok in re.findall(r"[a-z0-9]+", title.lower()) if len(tok) > 1}
        overlap = len(s_tokens & t_tokens)
        if overlap >= 2 and overlap > best_score:
            best_score = overlap
            best_title = title
    return best_title


def fetch_text_resource(url_or_path, label="Feed"):
    target = url_or_path.strip()
    if not target:
        return None, "Not configured"
    if os.path.isfile(target):
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            return f.read(), f"Local {label}"
    req = urllib.request.Request(
        target,
        headers={"User-Agent": "CentennialAcademicDashboard/1.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8", errors="replace"), label


def strip_emojis(text):
    cleaned = re.sub(r"[\U00010000-\U0010ffff\u2600-\u27bf\ufe0f]", "", str(text or ""))
    return re.sub(r"\s+", " ", cleaned).strip()


def fetch_json_resource(url, extra_headers=None, timeout=10):
    headers = {
        "User-Agent": "CentennialAcademicDashboard/1.0 (username: DeathSurvivor02)",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def parse_ics_dt_obj(raw_val):
    cleaned = (raw_val or "").strip()
    m = re.match(r"^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})(Z)?)?$", cleaned)
    if not m:
        return None
    yr, mo, dy = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hr = int(m.group(4) or 23)
    mn = int(m.group(5) or 59)
    sc = int(m.group(6) or 0)
    is_utc = m.group(7) == "Z"
    if is_utc:
        return datetime(yr, mo, dy, hr, mn, sc, tzinfo=timezone.utc).astimezone().replace(tzinfo=None)
    return datetime(yr, mo, dy, hr, mn, sc)


def parse_rrule_until(rrule_text):
    if not rrule_text:
        return None
    m = re.search(r"UNTIL=([0-9TZ]+)", rrule_text, re.IGNORECASE)
    if not m:
        return None
    return parse_ics_dt_obj(m.group(1))


def build_calendar_events_from_ics(events, src_label):
    now = datetime.now()
    window_start = now - timedelta(days=30)
    window_end = now + timedelta(days=60)
    cal_events = []
    seen_ids = set()

    for ev in events:
        summary = ev.get("SUMMARY", "").strip()
        desc = ev.get("DESCRIPTION", "").strip()
        cat = ev.get("CATEGORIES", "").strip()
        uid = ev.get("UID", "").strip()
        location = ev.get("LOCATION", "").strip()
        rrule = ev.get("RRULE", "").strip()
        if not summary:
            continue

        is_lecture = is_lecture_calendar_event(uid, summary)
        mapped_course_id, mapped_title = resolve_gradable_item(uid, summary)
        course_id = mapped_course_id or detect_course_id(" ".join([summary, cat, desc]))
        if not course_id:
            continue

        course_code = course_id.upper()
        dt_start = parse_ics_dt_obj(ev.get("DTSTART") or ev.get("DTEND"))
        dt_end = parse_ics_dt_obj(ev.get("DTEND") or ev.get("DTSTART"))
        if not dt_start:
            continue
        duration = (dt_end - dt_start) if (dt_end and dt_end >= dt_start) else timedelta(hours=1)

        if is_lecture:
            clean_title = re.sub(r"\s*\(SEC\.\s*\d+\)", "", summary, flags=re.IGNORECASE).strip()
            kind = "Class Session"
            event_url = f"{LUMINATE_BASE}/ultra/courses/{LUMINATE_COURSE_IDS.get(course_id, '')}/outline" if LUMINATE_COURSE_IDS.get(course_id) else f"{LUMINATE_BASE}/ultra/course"
        else:
            matched_title = mapped_title or match_baseline_title(course_id, summary)
            clean_title = matched_title or re.sub(r"\s*-\s*Due.*$", "", summary, flags=re.IGNORECASE).strip()
            kind = "Assessment"
            key = f"{course_id}::{clean_title}"
            event_url = SUBMISSION_URLS.get(key) or course_grades_url(course_id)

        occurrences = []
        if is_lecture and "FREQ=WEEKLY" in rrule.upper():
            until_dt = parse_rrule_until(rrule)
            end_limit = min(window_end, until_dt) if until_dt else window_end
            cur_dt = dt_start
            guard = 0
            while cur_dt <= end_limit and guard < 60:
                if cur_dt >= window_start:
                    occurrences.append(cur_dt)
                cur_dt = cur_dt + timedelta(days=7)
                guard += 1
            if not occurrences and window_start <= dt_start <= window_end:
                occurrences.append(dt_start)
        else:
            occurrences.append(dt_start)

        for occ_start in occurrences:
            occ_end = occ_start + duration
            date_key = occ_start.strftime("%Y-%m-%d")
            ev_id = hashlib.sha1(f"{course_code}|{kind}|{clean_title}|{date_key}|{occ_start.strftime('%H:%M')}".encode("utf-8")).hexdigest()[:12]
            if ev_id in seen_ids:
                continue
            seen_ids.add(ev_id)
            cal_events.append({
                "id": f"cal_{ev_id}",
                "courseId": course_id,
                "course": course_code,
                "title": clean_title,
                "kind": kind,
                "dateKey": date_key,
                "startIso": occ_start.strftime("%Y-%m-%dT%H:%M:%S"),
                "endIso": occ_end.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeLabel": occ_start.strftime("%H:%M") if is_lecture else occ_end.strftime("%H:%M"),
                "location": location,
                "details": desc[:200],
                "source": src_label,
                "url": event_url,
            })

    cal_events.sort(key=lambda x: x["startIso"])
    return cal_events


def sync_github_telemetry(config, state):
    username = (config.get("github_username") or "DeathSurvivor02").strip() or "DeathSurvivor02"
    prev = state.get("githubTelemetry") if isinstance(state.get("githubTelemetry"), dict) else {}
    token = (config.get("github_token") or os.environ.get("GITHUB_TOKEN") or "").strip()
    headers = {"User-Agent": "CentennialAcademicDashboard/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        user_data = fetch_json_resource(f"https://api.github.com/users/{urllib.parse.quote(username)}", headers)
        repos_raw = fetch_json_resource(
            f"https://api.github.com/users/{urllib.parse.quote(username)}/repos?sort=pushed&per_page=8",
            headers,
        )
        pr_count = prev.get("openPrs", 0)
        pr_items = prev.get("openPrItems", [])
        try:
            pr_query = urllib.parse.quote(f"author:{username} type:pr state:open")
            pr_data = fetch_json_resource(f"https://api.github.com/search/issues?q={pr_query}&per_page=5", headers)
            pr_count = int(pr_data.get("total_count", 0))
            pr_items = [
                {
                    "title": strip_emojis(it.get("title", "")),
                    "url": it.get("html_url", ""),
                    "number": it.get("number"),
                    "repo": (it.get("repository_url") or "").split("/")[-1],
                    "createdAt": (it.get("created_at") or "")[:10],
                }
                for it in (pr_data.get("items") or [])[:5]
            ]
        except Exception:
            pass

        repos = [
            {
                "name": r.get("name", ""),
                "fullName": r.get("full_name", ""),
                "description": strip_emojis((r.get("description") or "")[:120]),
                "language": r.get("language") or "Code",
                "stars": int(r.get("stargazers_count") or 0),
                "openIssues": int(r.get("open_issues_count") or 0),
                "defaultBranch": r.get("default_branch") or "main",
                "pushedAt": (r.get("pushed_at") or "")[:10],
                "url": r.get("html_url", ""),
            }
            for r in (repos_raw if isinstance(repos_raw, list) else [])[:8]
        ]

        state["githubTelemetry"] = {
            "username": user_data.get("login") or username,
            "profileUrl": user_data.get("html_url") or f"https://github.com/{username}",
            "publicRepos": int(user_data.get("public_repos") or len(repos)),
            "followers": int(user_data.get("followers") or 0),
            "openPrs": pr_count,
            "openPrItems": pr_items,
            "repos": repos,
            "status": "Live",
            "fetchedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return True, f"GitHub @{username} ({len(repos)} repos)"
    except Exception as exc:
        if prev:
            prev["status"] = f"Cached (offline: {type(exc).__name__})"
            state["githubTelemetry"] = prev
        else:
            state["githubTelemetry"] = {
                "username": username,
                "profileUrl": f"https://github.com/{username}",
                "publicRepos": 0,
                "followers": 0,
                "openPrs": 0,
                "openPrItems": [],
                "repos": [],
                "status": f"Unavailable ({type(exc).__name__})",
                "fetchedAt": "",
            }
        return False, f"GitHub offline ({type(exc).__name__})"


def sync_chess_telemetry(config, state):
    username = (config.get("chess_username") or "eanbynoe").strip().lower() or "eanbynoe"
    prev = state.get("chessTelemetry") if isinstance(state.get("chessTelemetry"), dict) else {}
    headers = {"User-Agent": f"CentennialAcademicDashboard/1.0 (username: {username})"}

    try:
        puzzle = fetch_json_resource("https://api.chess.com/pub/puzzle", headers)
        stats = {}
        try:
            stats = fetch_json_resource(f"https://api.chess.com/pub/player/{urllib.parse.quote(username)}/stats", headers)
        except Exception:
            pass
        to_move_games = []
        try:
            tm_resp = fetch_json_resource(f"https://api.chess.com/pub/player/{urllib.parse.quote(username)}/games/to-move", headers)
            to_move_games = tm_resp.get("games") or []
        except Exception:
            pass

        ratings = {
            "rapid": ((stats.get("chess_rapid") or {}).get("last") or {}).get("rating"),
            "blitz": ((stats.get("chess_blitz") or {}).get("last") or {}).get("rating"),
            "bullet": ((stats.get("chess_bullet") or {}).get("last") or {}).get("rating"),
            "daily": ((stats.get("chess_daily") or {}).get("last") or {}).get("rating"),
            "tactics": ((stats.get("tactics") or {}).get("highest") or {}).get("rating"),
        }
        state["chessTelemetry"] = {
            "username": username,
            "profileUrl": f"https://www.chess.com/member/{username}",
            "dailyPuzzle": {
                "title": strip_emojis(puzzle.get("title") or "Chess.com Daily Puzzle") or "Chess.com Daily Puzzle",
                "url": puzzle.get("url") or "https://www.chess.com/daily-chess-puzzle",
                "fen": puzzle.get("fen") or "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "pgn": puzzle.get("pgn") or "",
                "publishTime": puzzle.get("publish_time"),
            },
            "ratings": ratings,
            "gamesToMoveCount": len(to_move_games),
            "gamesToMove": [{"url": g.get("url", ""), "moveBy": g.get("move_by")} for g in to_move_games[:5]],
            "status": "Live",
            "fetchedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return True, f"Chess.com ({len(to_move_games)} to move)"
    except Exception as exc:
        if prev:
            prev["status"] = f"Cached (offline: {type(exc).__name__})"
            state["chessTelemetry"] = prev
        else:
            state["chessTelemetry"] = {
                "username": username,
                "profileUrl": f"https://www.chess.com/member/{username}",
                "dailyPuzzle": {
                    "title": "Daily Tactical Warmup",
                    "url": "https://www.chess.com/daily-chess-puzzle",
                    "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4",
                    "pgn": "",
                },
                "ratings": {},
                "gamesToMoveCount": 0,
                "gamesToMove": [],
                "status": f"Offline fallback ({type(exc).__name__})",
                "fetchedAt": "",
            }
        return False, f"Chess.com offline ({type(exc).__name__})"


def sync_wordle_daily(state):
    today_str = datetime.now().strftime("%Y-%m-%d")
    prev = state.get("wordleDaily") if isinstance(state.get("wordleDaily"), dict) else {}
    if prev.get("date") == today_str and isinstance(prev.get("solution"), str) and len(prev["solution"]) == 5:
        return True, f"Wordle {today_str} ({prev.get('source', 'Cached')})"

    try:
        data = fetch_json_resource(
            f"https://www.nytimes.com/svc/wordle/v2/{today_str}.json",
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        sol = str(data.get("solution") or "").strip().upper()
        if len(sol) == 5 and sol.isalpha():
            state["wordleDaily"] = {
                "date": today_str,
                "solution": sol,
                "daysSinceLaunch": data.get("days_since_launch"),
                "source": "NYT Wordle API",
                "fetchedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return True, f"Wordle {today_str} (NYT API)"
    except Exception:
        pass

    digest = int(hashlib.sha256(today_str.encode("utf-8")).hexdigest(), 16)
    fallback_word = WORDLE_FALLBACK_BANK[digest % len(WORDLE_FALLBACK_BANK)]
    state["wordleDaily"] = {
        "date": today_str,
        "solution": fallback_word,
        "daysSinceLaunch": None,
        "source": "Daily Word Bank",
        "fetchedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return True, f"Wordle {today_str} (Daily Bank)"


def scan_local_artifacts(config, overrides):
    sem5 = config.get("semester5_dir", "")
    downloads = config.get("downloads_dir", "")
    submissions_dir = os.path.join(BASE_DIR, "submissions")

    checks = [
        (
            "comp303::Assignment 3: Spring Boot REST App",
            [
                os.path.join(sem5, "Java", "EanBynoe_COMP303_Assign3.zip"),
                os.path.join(sem5, "Java", "EanBynoe_COMP303_Assignment3", "pom.xml"),
            ],
            "Packaged",
            True,
        ),
        (
            "comp309::COMP 309 Analytics Project (10%)",
            [
                os.path.join(sem5, "Data  Warehouse", "COMP309_Vehicle_Theft_Project.zip"),
                os.path.join(sem5, "Data  Warehouse", "COMP309_Bicycle_Theft_Project", "Theft_From_Motor_Vehicle_Project_Report.docx"),
            ],
            "Updated (Vehicle Theft)",
            True,
        ),
        (
            "comp307::Lab Assignment 6 (LFI/RFI)",
            [
                os.path.join(downloads, "COMP307_Lab_Assignment_6.docx"),
                os.path.join(submissions_dir, "Ean_Bynoe_COMP307_Lab6.pdf"),
            ],
            "Draft Ready",
            False,
        ),
        (
            "comp307::Research Project Submission",
            [
                os.path.join(downloads, "COMP307_Group12.pptx"),
                os.path.join(submissions_dir, "COMP307_Group12_OWASP_GenAI_LLM_Top10.pptx"),
            ],
            "Deck Ready",
            False,
        ),
        (
            "comp231::Progress Monitoring (Iteration 1)",
            [
                os.path.join(sem5, "COMP231_Iteration2_Planning_Package.md"),
            ],
            "Workspace Found",
            False,
        ),
        (
            "comp306::Cloud Engineering Project: Implementation",
            [
                os.path.join(sem5, "AWS", "CentennialRideLink", "README.md"),
            ],
            "Repo Active",
            False,
        ),
    ]

    detected = 0
    for key, candidate_paths, prefix, promote_ready in checks:
        for path in candidate_paths:
            if path and os.path.exists(path):
                fname = os.path.basename(path)
                cur = overrides.get(key, {})
                cur["localArtifact"] = f"{prefix}: {fname}"
                cur["localArtifactPath"] = os.path.abspath(path)
                if key in SUBMISSION_URLS:
                    cur["submissionUrl"] = SUBMISSION_URLS[key]
                if promote_ready and cur.get("status") not in ("GRADED", "SUBMITTED"):
                    cur["status"] = "READY"
                overrides[key] = cur
                detected += 1
                break
    return detected


def merge_luminate_feed(announcements, dismissed_ids):
    existing_map = {a.get("id"): idx for idx, a in enumerate(announcements) if a.get("id")}
    merged_count = 0
    for item in LUMINATE_COURSE_FEED:
        aid = item["id"]
        if aid in dismissed_ids:
            continue
        entry = {
            "id": aid,
            "course": item["course"],
            "kind": item["kind"],
            "title": item["title"],
            "body": item["body"],
            "timestamp": item["timestamp"],
            "source": item["source"],
            "url": item.get("url", ""),
            "urgent": bool(item.get("urgent", False)),
            "pinned": bool(item.get("pinned", False)),
            "read": False,
        }
        if aid in existing_map:
            idx = existing_map[aid]
            entry["read"] = announcements[idx].get("read", False)
            entry["pinned"] = announcements[idx].get("pinned", entry["pinned"])
            announcements[idx] = entry
        else:
            existing_map[aid] = len(announcements)
            announcements.append(entry)
        merged_count += 1
    return merged_count


def sync():
    config = load_json(
        CONFIG_PATH,
        {
            "ics_feed_url": "",
            "rss_feeds": [],
            "semester5_dir": "",
            "downloads_dir": "",
            "github_username": "DeathSurvivor02",
            "chess_username": "eanbynoe",
            "auto_sync_on_startup": True,
        },
    )
    state = load_json(
        STATE_PATH,
        {
            "overrides": {},
            "customItems": [],
            "announcements": [],
            "dismissedAnnouncementIds": [],
            "calendarEvents": [],
            "posStatuses": {},
        },
    )
    overrides = state.setdefault("overrides", {})
    custom_items = state.setdefault("customItems", [])
    announcements = state.setdefault("announcements", [])
    dismissed_ids = set(state.get("dismissedAnnouncementIds") or [])

    # Drop legacy comp231::Evaluation 6 override once migrated to Progress Monitoring (Iteration 1)
    overrides.pop("comp231::Evaluation 6: Working Prototype / Code (Iteration 1)", None)
    # Sync COMP307 submitted items so local drafts do not override Luminate Submitted state
    for sub_key in ("comp307::Lab Assignment 6 (LFI/RFI)", "comp307::Research Project Submission"):
        if sub_key in overrides and overrides[sub_key].get("status") == "READY":
            overrides[sub_key]["status"] = "SUBMITTED"

    ics_status = "No .ics feed URL configured"
    ics_updated = 0
    cal_count = len(state.get("calendarEvents") or [])
    feed_url = config.get("ics_feed_url", "").strip()
    if feed_url:
        try:
            raw_ics, src_label = fetch_text_resource(feed_url, "eCentennial .ics")
            events = parse_ics_events(raw_ics or "")
            state["calendarEvents"] = build_calendar_events_from_ics(events, src_label)
            cal_count = len(state["calendarEvents"])

            # Remove recurring class lecture entries previously synced from calendar
            custom_items[:] = [
                item for item in custom_items
                if not re.search(r"\(SEC\.\s*\d+\)", item.get("name", ""), re.IGNORECASE)
            ]
            existing_custom_map = {
                (item.get("courseId"), item.get("name")): idx
                for idx, item in enumerate(custom_items)
            }
            for ev in events:
                summary = ev.get("SUMMARY", "")
                desc = ev.get("DESCRIPTION", "")
                cat = ev.get("CATEGORIES", "")
                uid = ev.get("UID", "")
                if is_lecture_calendar_event(uid, summary):
                    continue

                mapped_course_id, mapped_title = resolve_gradable_item(uid, summary)
                course_id = mapped_course_id or detect_course_id(" ".join([summary, cat, desc]))
                if not course_id:
                    continue
                dt_raw = ev.get("DTEND") or ev.get("DTSTART") or ""
                parsed_dt = parse_ics_datetime(dt_raw)
                due_iso, due_label = parsed_dt if parsed_dt else ("", "From eCentennial")

                matched_title = mapped_title or match_baseline_title(course_id, summary)
                if matched_title:
                    key = f"{course_id}::{matched_title}"
                    cur = overrides.get(key, {})
                    if due_iso:
                        cur["dueIso"] = due_iso
                        cur["due"] = due_label
                    if desc and not cur.get("details"):
                        cur["details"] = desc[:240]
                    cur["syncedSource"] = src_label
                    cur["submissionUrl"] = SUBMISSION_URLS.get(key) or cur.get("submissionUrl") or course_grades_url(course_id)
                    overrides[key] = cur
                    ics_updated += 1
                else:
                    clean_name = re.sub(r"\s*-\s*Due.*$", "", summary, flags=re.IGNORECASE).strip()
                    ck = (course_id, clean_name)
                    item_obj = {
                        "courseId": course_id,
                        "name": clean_name,
                        "details": desc[:240] if desc else f"Synced from {src_label}",
                        "weight": "-",
                        "due": due_label,
                        "dueIso": due_iso,
                        "score": "-",
                        "total": "100",
                        "pct": "-",
                        "status": "PENDING",
                        "syncedSource": src_label,
                        "submissionUrl": course_grades_url(course_id),
                    }
                    if ck in existing_custom_map:
                        idx = existing_custom_map[ck]
                        prev = custom_items[idx]
                        item_obj["status"] = prev.get("status", "PENDING")
                        item_obj["score"] = prev.get("score", "-")
                        item_obj["pct"] = prev.get("pct", "-")
                        custom_items[idx] = item_obj
                    else:
                        existing_custom_map[ck] = len(custom_items)
                        custom_items.append(item_obj)
                    ics_updated += 1
            ics_status = f"Synced {ics_updated} assessment items & {cal_count} calendar events from {src_label}"
        except Exception as exc:
            ics_status = f"ICS feed error: {exc}"

    rss_count = merge_luminate_feed(announcements, dismissed_ids)
    rss_feeds = config.get("rss_feeds") or []
    existing_ann_map = {a.get("id"): idx for idx, a in enumerate(announcements) if a.get("id")}
    for feed_entry in rss_feeds:
        url = feed_entry.strip() if isinstance(feed_entry, str) else ""
        if not url:
            continue
        try:
            raw_xml, src_label = fetch_text_resource(url, "Class RSS")
            parsed_anns = parse_rss_announcements(raw_xml or "", src_label)
            for ann in parsed_anns:
                if ann["id"] in dismissed_ids:
                    continue
                if ann["id"] in existing_ann_map:
                    idx = existing_ann_map[ann["id"]]
                    ann["read"] = announcements[idx].get("read", False)
                    ann["pinned"] = announcements[idx].get("pinned", False)
                    announcements[idx] = ann
                else:
                    existing_ann_map[ann["id"]] = len(announcements)
                    announcements.insert(0, ann)
                rss_count += 1
        except Exception:
            pass

    detected_artifacts = scan_local_artifacts(config, overrides)

    _, gh_summary = sync_github_telemetry(config, state)
    _, chess_summary = sync_chess_telemetry(config, state)
    _, wordle_summary = sync_wordle_daily(state)

    state["lastSyncedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rss_part = f" | {rss_count} announcements & discussions"
    state["lastSyncSummary"] = (
        f"{ics_status}{rss_part} | {detected_artifacts} local deliverables | "
        f"{gh_summary} | {chess_summary} | {wordle_summary}"
    )
    save_json(STATE_PATH, state)
    print(state["lastSyncSummary"])


if __name__ == "__main__":
    sync()
