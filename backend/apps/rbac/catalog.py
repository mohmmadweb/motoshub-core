"""
The canonical permission catalog — mirrors the prototype's `permissionCatalog`
(20 groups). This lives in code (not the DB): each id is `"<group>.<action>"`.
New modules append their group here. `seed_rbac` writes preset roles from it.
"""

PERMISSION_CATALOG = [
    ("users", "کاربران", ["list", "create", "edit", "import", "block", "guest"]),
    ("roles", "نقش‌ها و دسترسی‌ها", ["list", "create", "edit", "delete", "assign"]),
    ("news", "اخبار", ["list", "create", "edit", "delete", "pin", "comments"]),
    ("blog", "بلاگ", ["list", "create", "edit", "delete", "comments"]),
    ("groups", "گروه‌ها", ["list", "create", "edit", "delete", "members", "post"]),
    ("forum", "تالار گفتگو", ["list", "create", "reply", "edit", "delete", "solve"]),
    ("events", "رویدادها", ["list", "create", "edit", "delete", "invite"]),
    ("media", "رسانه", ["list", "upload", "edit", "delete", "albums"]),
    ("chat", "گفتگو", ["view", "channels", "pin", "integrations"]),
    ("knowledge", "مدیریت دانش", ["list", "upload", "edit", "delete", "categories", "visibility"]),
    ("projects", "پروژه‌ها", ["list", "create", "edit", "delete", "tasks", "progress"]),
    ("contracts", "قراردادها", ["list", "create", "edit", "delete", "stage"]),
    ("funds", "صندوق‌ها", ["list", "submit", "refer", "score", "allocate", "monitor"]),
    ("research", "پژوهش", ["list", "create", "edit", "close"]),
    ("reports", "گزارش‌گیری", ["view", "export"]),
    ("training", "آموزش", ["list", "create", "enroll", "evaluate", "certificate"]),
    ("companies", "هلدینگ‌ها و شرکت‌ها", ["view", "manage", "publish-global", "publish-holding"]),
    ("assistant", "دستیار هوشمند", ["chat", "evaluate", "configure"]),
    ("award", "جایزه نوآوری", ["list", "validate", "judge", "score"]),
    ("settings", "تنظیمات", ["branding", "modules", "pages", "security", "system", "storage"]),
]


def all_permission_ids() -> list[str]:
    ids = []
    for group, _label, actions in PERMISSION_CATALOG:
        ids.extend(f"{group}.{action}" for action in actions)
    return ids


# Preset (system) roles — non-deletable. Mirrors prototype r1..r4.
def preset_roles() -> list[dict]:
    every = all_permission_ids()
    return [
        {
            "key": "platform-admin",
            "title": "راهبر پلتفرم",
            "scope": "platform",
            "permissions": every,
        },
        {
            "key": "org-admin",
            "title": "مدیر سازمان",
            "scope": "tenant",
            "permissions": [p for p in every if not p.startswith(("settings.system", "settings.storage"))],
        },
        {
            "key": "group-moderator",
            "title": "ناظم گروه",
            "scope": "group",
            "permissions": [
                "groups.list", "groups.edit", "groups.members", "groups.post",
                "forum.list", "forum.create", "forum.reply", "forum.solve",
                "chat.view", "chat.pin", "media.list", "media.upload",
                "news.list", "blog.list", "events.list",
            ],
        },
        {
            "key": "member",
            "title": "عضو عادی",
            "scope": "group",
            "permissions": [
                "news.list", "blog.list", "groups.list", "groups.post",
                "forum.list", "forum.reply", "events.list", "media.list",
                "chat.view", "knowledge.list", "reports.view",
            ],
        },
    ]
