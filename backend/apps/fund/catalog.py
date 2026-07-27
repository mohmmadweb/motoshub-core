"""Innovation-fund state machine catalog (mirrors nfStages / nfSubStatuses)."""

NF_STAGES = [
    ("proposal", "دریافت پروپوزال"),
    ("screening", "ارزیابی اولیه"),
    ("jury", "ارزیابی موشکافانه"),
    ("approval", "تصویب طرح"),
    ("contract", "تنظیم قرارداد"),
    ("monitoring", "نظارت و راهبری"),
    ("exit", "خروج از صندوق"),
]
NF_STAGE_ORDER = [k for k, _ in NF_STAGES]

# Evaluation thresholds (defaults; overridable per-tenant later via settings).
SCREENING_MAX, SCREENING_THRESHOLD = 200, 80
JURY_MAX, JURY_THRESHOLD = 100, 50
REVIEW_ESCALATION_DAYS = 15
