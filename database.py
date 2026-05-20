import aiosqlite
import asyncio
from datetime import datetime

DB_PATH = "kino_bot.db"

class Database:
    def __init__(self):
        self.db_path = DB_PATH

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Foydalanuvchilar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    username TEXT,
                    full_name TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_blocked INTEGER DEFAULT 0,
                    ref_code TEXT,
                    joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_active TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Kinolar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE,
                    file_id TEXT,
                    name TEXT,
                    access_type TEXT DEFAULT 'all',
                    views INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Kanallar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT UNIQUE,
                    channel_name TEXT,
                    channel_type TEXT DEFAULT 'public',
                    channel_url TEXT,
                    added_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Referal havolalar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    code TEXT UNIQUE,
                    user_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Referal foydalanuvchilar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS referral_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referral_id INTEGER,
                    user_id INTEGER,
                    joined_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Reklamalar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    file_type TEXT,
                    caption TEXT,
                    button_text TEXT,
                    button_url TEXT,
                    show_on_start INTEGER DEFAULT 0,
                    show_on_movie INTEGER DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Top 10
            await db.execute("""
                CREATE TABLE IF NOT EXISTS top_movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movie_code TEXT,
                    movie_name TEXT,
                    position INTEGER,
                    added_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Sozlamalar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            # So'rovlar
            await db.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Default sozlamalar
            defaults = [
                ("start_text", "👋 Assalomu alaykum {name} botimizga xush kelibsiz.\n\n✍🏻 Kino kodini yuboring."),
                ("channel_text", "❌ Kechirasiz, botimizdan foydalanish uchun ushbu kanallarga obuna bo'lishingiz kerak."),
                ("subscribe_btn", "➕ Obuna bo'lish"),
                ("check_btn", "✅ Tasdiqlash"),
                ("movie_caption", "🔍 Kino kodi: {code}\n\n{name}\n\n🤖 Botimiz: @{bot}\n\n👁 Ko'rishlar: {views} ta"),
                ("share_btn", "↗️ Ulashish"),
                ("movie_parts_title", "🎬 Kino qismlari ro'yxati:"),
                ("wrong_code_text", "❌ Kino kodini noto'g'ri yubordingiz!"),
                ("part_name", "{part}-qism"),
                ("movie_name_text", "🎬 Nomi:"),
                ("discussion_url", ""),
                ("forward_protection_users", "1"),
                ("forward_protection_premium", "1"),
                ("auto_approve", "0"),
                ("approve_post", ""),
            ]
            for key, value in defaults:
                await db.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (key, value)
                )

            await db.commit()

    # ============ USERS ============
    async def add_user(self, user_id, username, full_name, ref_code=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, username, full_name, ref_code)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, full_name, ref_code))
            await db.commit()

    async def get_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE is_blocked = 0") as cursor:
                return await cursor.fetchall()

    async def get_users_page(self, page=0, per_page=10):
        async with aiosqlite.connect(self.db_path) as db:
            offset = page * per_page
            async with db.execute(
                "SELECT * FROM users ORDER BY joined_at DESC LIMIT ? OFFSET ?",
                (per_page, offset)
            ) as cursor:
                return await cursor.fetchall()

    async def get_users_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                return (await cursor.fetchone())[0]

    async def get_active_users_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users WHERE is_active = 1 AND is_blocked = 0") as cursor:
                return (await cursor.fetchone())[0]

    async def get_left_users_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users WHERE is_active = 0") as cursor:
                return (await cursor.fetchone())[0]

    async def get_blocked_users_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1") as cursor:
                return (await cursor.fetchone())[0]

    async def get_new_users_count(self, hours=24):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                f"SELECT COUNT(*) FROM users WHERE joined_at >= datetime('now', '-{hours} hours')"
            ) as cursor:
                return (await cursor.fetchone())[0]

    async def get_active_users_in_period(self, hours=24):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                f"SELECT COUNT(*) FROM users WHERE last_active >= datetime('now', '-{hours} hours')"
            ) as cursor:
                return (await cursor.fetchone())[0]

    async def update_last_active(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET last_active = CURRENT_TIMESTAMP, is_active = 1 WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()

    async def set_user_active(self, user_id, is_active):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_active = ? WHERE user_id = ?",
                (is_active, user_id)
            )
            await db.commit()

    async def block_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_blocked = 1 WHERE user_id = ?", (user_id,)
            )
            await db.commit()

    async def delete_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            await db.commit()

    async def get_blocked_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE is_blocked = 1") as cursor:
                return await cursor.fetchall()

    async def search_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()

    # ============ MOVIES ============
    async def add_movie(self, code, file_id, name, access_type='all'):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO movies (code, file_id, name, access_type)
                VALUES (?, ?, ?, ?)
            """, (code, file_id, name, access_type))
            await db.commit()

    async def get_movie(self, code):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM movies WHERE code = ?", (code,)) as cursor:
                return await cursor.fetchone()

    async def get_all_movies(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM movies ORDER BY created_at DESC") as cursor:
                return await cursor.fetchall()

    async def get_movies_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM movies") as cursor:
                return (await cursor.fetchone())[0]

    async def update_movie(self, code, name):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE movies SET name = ? WHERE code = ?", (name, code))
            await db.commit()

    async def delete_movie(self, code):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM movies WHERE code = ?", (code,))
            await db.commit()

    async def increment_views(self, code):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE movies SET views = views + 1 WHERE code = ?", (code,))
            await db.commit()

    async def get_downloads_count(self, hours=24):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                f"SELECT SUM(views) FROM movies"
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] or 0

    # ============ CHANNELS ============
    async def add_channel(self, channel_id, channel_name, channel_type, channel_url):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO channels (channel_id, channel_name, channel_type, channel_url)
                VALUES (?, ?, ?, ?)
            """, (channel_id, channel_name, channel_type, channel_url))
            await db.commit()

    async def get_all_channels(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM channels") as cursor:
                return await cursor.fetchall()

    async def delete_channel(self, channel_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            await db.commit()

    async def channel_exists(self, channel_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id FROM channels WHERE channel_id = ?", (channel_id,)) as cursor:
                return await cursor.fetchone() is not None

    # ============ REFERRALS ============
    async def add_referral(self, name, code):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO referrals (name, code) VALUES (?, ?)", (name, code)
            )
            await db.commit()

    async def get_all_referrals(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM referrals ORDER BY created_at DESC") as cursor:
                return await cursor.fetchall()

    async def get_referral_by_code(self, code):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM referrals WHERE code = ?", (code,)) as cursor:
                return await cursor.fetchone()

    async def delete_referral(self, ref_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM referrals WHERE id = ?", (ref_id,))
            await db.commit()

    async def add_referral_user(self, referral_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO referral_users (referral_id, user_id) VALUES (?, ?)",
                (referral_id, user_id)
            )
            await db.execute(
                "UPDATE referrals SET user_count = user_count + 1 WHERE id = ?",
                (referral_id,)
            )
            await db.commit()

    async def get_total_referrals_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM referrals") as cursor:
                return (await cursor.fetchone())[0]

    async def get_total_referral_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT SUM(user_count) FROM referrals") as cursor:
                result = await cursor.fetchone()
                return result[0] or 0

    async def get_user_referral_link(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT ref_code FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

    async def get_user_referral_count(self, ref_code):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE ref_code = ?", (ref_code,)
            ) as cursor:
                return (await cursor.fetchone())[0]

    # ============ ADS ============
    async def add_ad(self, file_id, file_type, caption, button_text=None, button_url=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO ads (file_id, file_type, caption, button_text, button_url)
                VALUES (?, ?, ?, ?, ?)
            """, (file_id, file_type, caption, button_text, button_url))
            await db.commit()

    async def get_all_ads(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM ads ORDER BY created_at DESC") as cursor:
                return await cursor.fetchall()

    async def get_active_ads(self, show_type='start'):
        async with aiosqlite.connect(self.db_path) as db:
            col = "show_on_start" if show_type == 'start' else "show_on_movie"
            async with db.execute(f"SELECT * FROM ads WHERE {col} = 1") as cursor:
                return await cursor.fetchall()

    async def toggle_ad_setting(self, ad_type):
        key = f"ads_{ad_type}"
        current = await self.get_setting(key)
        new_val = "0" if current == "1" else "1"
        await self.set_setting(key, new_val)
        return new_val

    async def get_ads_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM ads") as cursor:
                return (await cursor.fetchone())[0]

    # ============ TOP 10 ============
    async def add_top_movie(self, movie_code, movie_name):
        async with aiosqlite.connect(self.db_path) as db:
            count = await self.get_top_count()
            await db.execute("""
                INSERT INTO top_movies (movie_code, movie_name, position)
                VALUES (?, ?, ?)
            """, (movie_code, movie_name, count + 1))
            await db.commit()

    async def get_top_movies(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM top_movies ORDER BY position") as cursor:
                return await cursor.fetchall()

    async def get_top_count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM top_movies") as cursor:
                return (await cursor.fetchone())[0]

    async def delete_top_movie(self, movie_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM top_movies WHERE id = ?", (movie_id,))
            await db.commit()

    # ============ SETTINGS ============
    async def get_setting(self, key):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

    async def set_setting(self, key, value):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            await db.commit()

    # ============ ADMINS ============
    async def add_admin(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (f"admin_{user_id}", "1")
            )
            await db.commit()

    async def remove_admin(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM settings WHERE key = ?", (f"admin_{user_id}",)
            )
            await db.commit()

    async def get_all_admins(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT key FROM settings WHERE key LIKE 'admin_%'"
            ) as cursor:
                rows = await cursor.fetchall()
                return [int(row[0].replace("admin_", "")) for row in rows]

    async def is_admin(self, user_id):
        from config import ADMIN_IDS
        if user_id in ADMIN_IDS:
            return True
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT value FROM settings WHERE key = ?", (f"admin_{user_id}",)
            ) as cursor:
                return await cursor.fetchone() is not None

    # ============ REQUESTS ============
    async def add_request(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO requests (user_id) VALUES (?)", (user_id,)
            )
            await db.commit()

    async def get_pending_requests(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM requests WHERE status = 'pending'"
            ) as cursor:
                return await cursor.fetchall()

    async def approve_request(self, request_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE requests SET status = 'approved' WHERE id = ?", (request_id,)
            )
            await db.commit()

db = Database()
