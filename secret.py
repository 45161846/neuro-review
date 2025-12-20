import secrets
import base64

secret = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
print(f"Ваш секрет для GitHub Webhook: {secret}")
print("\nДобавьте эту строку в ваш .env файл:")
print(f"GITHUB_WEBHOOK_SECRET={secret}")