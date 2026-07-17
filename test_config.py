from app.core.config import settings

print("=" * 50)
print("TEVANOXMOVIE - Configuration Test")
print("=" * 50)
print("\nConfig loaded successfully!")
print("\nDatabase Configuration:")
print(f"  MONGO_URI: {settings.MONGO_URI}")
print(f"  MONGO_DB_NAME: {settings.MONGO_DB_NAME}")

print("\nSecurity:")
print(f"  SECRET_KEY: {settings.SECRET_KEY[:10]}... (length: {len(settings.SECRET_KEY)})")
print(f"  ALGORITHM: {settings.ALGORITHM}")
print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")

print("\nDomain Configuration:")
print(f"  DOMAIN: {settings.DOMAIN}")
print(f"  API_URL: {settings.API_URL}")
print(f"  WEB_URL: {settings.WEB_URL}")
print(f"  ADMIN_URL: {settings.ADMIN_URL}")

print("\nStorage:")
print(f"  STORAGE_ENDPOINT: {settings.STORAGE_ENDPOINT}")
print(f"  STORAGE_BUCKET: {settings.STORAGE_BUCKET}")

print("\nCommission Rates:")
print(f"  TEVANOX_SHARE: {settings.TEVANOX_SHARE}")
print(f"  NETWORK_TOTAL: {settings.NETWORK_TOTAL}")
print(f"  LEVEL_1_COMMISSION: {settings.LEVEL_1_COMMISSION}")
print(f"  LEVEL_2_COMMISSION: {settings.LEVEL_2_COMMISSION}")
print(f"  LEVEL_3_COMMISSION: {settings.LEVEL_3_COMMISSION}")

print("\nPayment:")
print(f"  PAYSTACK_PUBLIC_KEY: {settings.PAYSTACK_PUBLIC_KEY[:10]}...")

print("\nAllowed Origins:")
for origin in settings.ALLOWED_ORIGINS:
    print(f"  - {origin}")

print("\n" + "=" * 50)
print("Configuration test completed successfully!")
print("=" * 50)
