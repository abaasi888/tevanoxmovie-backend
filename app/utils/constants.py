# ============================================================================ #
#                         APPLICATION CONSTANTS                               #
# ============================================================================ #

# Content Categories
MOVIE_CATEGORIES = {
    "UGANDAN": "ugandan",
    "ENGLISH": "english",
    "LUGANDA_TRANSLATED": "luganda_translated",
    "SWAHILI_TRANSLATED": "swahili_translated",
}

MUSIC_CATEGORIES = {
    "UGANDAN": "ugandan",
    "INTERNATIONAL": "international",
}

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "weekly": {"duration": 7, "price": 7000},
    "biweekly": {"duration": 14, "price": 12000},
    "monthly": {"duration": 30, "price": 20000},
}

# Commission Rates
COMMISSION_RATES = {
    "TEVANOX_SHARE": 0.60,
    "NETWORK_TOTAL": 0.40,
    "LEVEL_1": 0.25,
    "LEVEL_2": 0.10,
    "LEVEL_3": 0.05,
}

# Agent Tiers
AGENT_TIERS = [
    {"tier": 1, "min_users": 0, "max_users": 100, "commission_rate": 0.15, "bonus": 0},
    {"tier": 2, "min_users": 101, "max_users": 500, "commission_rate": 0.12, "bonus": 50000},
    {"tier": 3, "min_users": 501, "max_users": 999, "commission_rate": 0.10, "bonus": 100000},
    {"tier": 4, "min_users": 1000, "max_users": float("inf"), "commission_rate": 0.08, "bonus": 200000},
]

# Payment Methods
PAYMENT_METHODS = {
    "MOBILE_MONEY": "mobile_money",
    "VISA": "visa",
    "BANK_TRANSFER": "bank_transfer",
}

# Content Types
CONTENT_TYPES = {
    "MOVIE": "movie",
    "SERIES": "series",
    "MUSIC": "music",
    "EPISODE": "episode",
}

# User Roles
USER_ROLES = {
    "USER": "user",
    "AGENT": "agent",
    "ADMIN": "admin",
    "VJ": "vj",
    "ARTIST": "artist",
}