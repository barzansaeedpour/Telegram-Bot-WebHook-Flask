# add_user.py
from db import SessionLocal, TelegramUser

db = SessionLocal()
user = TelegramUser(telegram_user_id="78163240", sazman_id="14")
db.add(user)
db.commit()
db.close()
print("User added.")
