from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============ ADMIN KEYBOARDS ============

def admin_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="✉️ Xabar yuborish", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton(text="🎬 Kontent boshqaruvi", callback_data="admin_content"),
            InlineKeyboardButton(text="🔑 Kanallar", callback_data="admin_channels"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Tizim sozlamalari", callback_data="admin_settings"),
            InlineKeyboardButton(text="📩 So'rovlar", callback_data="admin_requests"),
        ],
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="🏆 Top 10", callback_data="admin_top10"),
        ],
        [
            InlineKeyboardButton(text="💬 Muhokama", callback_data="admin_discussion"),
        ],
    ])

def admin_content_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Kinolar", callback_data="admin_movies")],
        [InlineKeyboardButton(text="📌 Postlar", callback_data="admin_posts")],
        [InlineKeyboardButton(text="🔗 Referal", callback_data="admin_referral")],
        [InlineKeyboardButton(text="◀️ Asosiy panel", callback_data="admin_main")],
    ])

def admin_movies_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Kino yuklash", callback_data="movie_upload")],
        [
            InlineKeyboardButton(text="📝 Kino tahrirlash", callback_data="movie_edit"),
            InlineKeyboardButton(text="🗑 Kino o'chirish", callback_data="movie_delete"),
        ],
        [InlineKeyboardButton(text="📋 Kinolar ro'yxati", callback_data="movie_list")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_content")],
    ])

def movie_access_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔒 Hammaga", callback_data="movie_access_all")],
        [InlineKeyboardButton(text="💎 Faqat Premium", callback_data="movie_access_premium")],
    ])

def movie_upload_confirm_kb(code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="+ Nom kiritish", callback_data=f"movie_add_name_{code}")],
        [InlineKeyboardButton(text="📤 Yuklash: 🔒 Hammaga", callback_data=f"movie_save_all_{code}")],
        [InlineKeyboardButton(text="📤 Yuklash: 💎 Premium", callback_data=f"movie_save_premium_{code}")],
    ])

def admin_channels_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="+ Kanal qo'shish", callback_data="channel_add")],
        [InlineKeyboardButton(text="📋 Ro'yxatni ko'rish", callback_data="channel_list")],
        [InlineKeyboardButton(text="🗑 Kanalni o'chirish", callback_data="channel_delete")],
    ])

def channel_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Ommaviy / Shaxsiy (Kanal · Guruh)", callback_data="ch_type_public")],
        [InlineKeyboardButton(text="🔑 Shaxsiy / So'rovli havola", callback_data="ch_type_private")],
        [InlineKeyboardButton(text="🌐 Oddiy havola", callback_data="ch_type_link")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_channels")],
    ])

def admin_settings_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 Reklama", callback_data="settings_ads"),
            InlineKeyboardButton(text="👮 Adminlar", callback_data="settings_admins"),
        ],
        [InlineKeyboardButton(text="📝 Matnlar", callback_data="settings_texts")],
        [InlineKeyboardButton(text="◀️ Asosiy panel", callback_data="admin_main")],
    ])

def admin_ads_kb(start_status, movie_status):
    start_icon = "✅" if start_status == "1" else "❌"
    movie_icon = "✅" if movie_status == "1" else "❌"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"🚀 Start: {start_icon}", callback_data="ads_toggle_start"),
            InlineKeyboardButton(text=f"🎬 Kino: {movie_icon}", callback_data="ads_toggle_movie"),
        ],
        [InlineKeyboardButton(text="+ Reklama qo'shish", callback_data="ads_add")],
        [InlineKeyboardButton(text="📋 Reklamalar ro'yxati", callback_data="ads_list")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_settings")],
    ])

def ad_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⊞ Tugma qo'shish", callback_data="ad_add_button")],
        [InlineKeyboardButton(text="✅ Saqlash", callback_data="ad_save")],
        [InlineKeyboardButton(text="🗑 Bekor qilish", callback_data="ad_cancel")],
    ])

def admin_admins_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="+ Admin qo'shish", callback_data="admin_add"),
            InlineKeyboardButton(text="— Adminni o'chirish", callback_data="admin_remove"),
        ],
        [InlineKeyboardButton(text="📋 Adminlar ro'yxati", callback_data="admin_list")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_settings")],
    ])

def admin_texts_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👋 Start xabari", callback_data="text_start")],
        [InlineKeyboardButton(text="📢 Kanallar chiqadigan matn", callback_data="text_channel")],
        [InlineKeyboardButton(text="+ Obuna bo'lish tugmasi", callback_data="text_subscribe_btn")],
        [InlineKeyboardButton(text="✅ Tekshirish tugmasi", callback_data="text_check_btn")],
        [InlineKeyboardButton(text="🎬 Kino caption matni", callback_data="text_movie_caption")],
        [InlineKeyboardButton(text="↗️ Ulashish tugmasi", callback_data="text_share_btn")],
        [InlineKeyboardButton(text="🎬 Kino qismlari sarlavhasi", callback_data="text_parts_title")],
        [InlineKeyboardButton(text="❌ Noto'g'ri kod xabari", callback_data="text_wrong_code")],
        [InlineKeyboardButton(text="🎞️ Qism nomi", callback_data="text_part_name")],
        [InlineKeyboardButton(text="🎬 Kino nomi matni", callback_data="text_movie_name")],
        [InlineKeyboardButton(text="🔄 Hammasini asliga qaytarish", callback_data="text_reset_all")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_settings")],
    ])

def text_edit_kb(key):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Asliga qaytarish", callback_data=f"text_reset_{key}")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="settings_texts")],
    ])

def text_reset_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, qaytarish", callback_data="text_reset_confirm")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_texts")],
    ])

def admin_users_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Foydalanuvchilar ro'yxati", callback_data="users_list_0")],
        [InlineKeyboardButton(text="🔍 Foydalanuvchi qidirish", callback_data="users_search")],
        [InlineKeyboardButton(text="🚫 Bloklangan foydalanuvchilar", callback_data="users_blocked")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_main")],
    ])

def user_actions_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"user_block_{user_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"user_delete_{user_id}")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_users")],
    ])

def admin_top10_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Kino qo'shish", callback_data="top10_add")],
        [InlineKeyboardButton(text="📋 Ro'yxat", callback_data="top10_list")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data="top10_delete")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_main")],
    ])

def admin_discussion_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Guruh havolasini o'rnatish", callback_data="discussion_set")],
        [InlineKeyboardButton(text="✏️ Havolani tahrirlash", callback_data="discussion_edit")],
        [InlineKeyboardButton(text="🗑 Havolani o'chirish", callback_data="discussion_delete")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_main")],
    ])

def admin_referral_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="+ Havola yaratish", callback_data="ref_create")],
        [InlineKeyboardButton(text="📋 Havolalar ro'yxati", callback_data="ref_list")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_content")],
    ])

def referral_actions_kb(ref_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="+ Yana yaratish", callback_data="ref_create")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"ref_delete_{ref_id}")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="ref_list")],
    ])

def admin_posts_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Yangi post yaratish", callback_data="post_create")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_content")],
    ])

def post_channel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ ID/username/forward - kiritish", callback_data="post_enter_channel")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_posts")],
    ])

def broadcast_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Oddiy", callback_data="broadcast_normal"),
            InlineKeyboardButton(text="📨 Forward", callback_data="broadcast_forward"),
        ],
    ])

def broadcast_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⊞ Tugma qo'shish", callback_data="broadcast_add_button")],
        [InlineKeyboardButton(text="✅ Yuborishni boshlash", callback_data="broadcast_send")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")],
    ])

def forward_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yuborishni boshlash", callback_data="broadcast_send_forward")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")],
    ])

def requests_kb(auto_approve):
    status = "✅ Yoqiq" if auto_approve == "1" else "❌ O'chiq"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⚡ Avto tasdiqlash: {status}", callback_data="requests_toggle_auto")],
        [InlineKeyboardButton(text="📨 Post belgilash", callback_data="requests_set_post")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_main")],
    ])

def back_to_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_main")],
    ])

def users_list_kb(page, total, per_page=10):
    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"users_list_{page-1}"))
    total_pages = (total + per_page - 1) // per_page
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"users_list_{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_users")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def channel_delete_kb(channels):
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"🗑 {ch[2]}", callback_data=f"ch_delete_{ch[1]}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_channels")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def top10_delete_kb(movies):
    buttons = []
    for m in movies:
        buttons.append([InlineKeyboardButton(
            text=f"🗑 {m[3]}. {m[2]}", callback_data=f"top10_del_{m[0]}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_top10")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def movie_delete_kb(movies):
    buttons = []
    for m in movies:
        buttons.append([InlineKeyboardButton(
            text=f"🗑 [{m[1]}] {m[3] or 'Nomsiz'}", callback_data=f"movie_del_{m[1]}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_movies")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ============ USER KEYBOARDS ============

def user_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔍 Qidiruv"), KeyboardButton(text="🏆 Top 10")],
        [KeyboardButton(text="💬 Muhokama"), KeyboardButton(text="📢 Reklama")],
        [KeyboardButton(text="🔗 Referal")],
    ], resize_keyboard=True)

def subscribe_kb(channels, bot_username):
    buttons = []
    for ch in channels:
        ch_id, ch_name, ch_type, ch_url = ch[1], ch[2], ch[3], ch[4]
        if ch_url:
            buttons.append([InlineKeyboardButton(text=f"📢 {ch_name}", url=ch_url)])
        else:
            buttons.append([InlineKeyboardButton(text=f"📢 {ch_name}", url=f"https://t.me/{ch_id.replace('@', '')}")])
    buttons.append([InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="check_subscribe")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def movie_share_kb(code, bot_username, share_text):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=share_text,
            url=f"https://t.me/share/url?url=https://t.me/{bot_username}?start={code}"
        )],
    ])
