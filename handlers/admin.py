from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
import secrets
from database import db
from keyboards import *
from config import ADMIN_IDS

router = Router()

# ============ STATES ============
class AdminStates(StatesGroup):
    # Movie
    waiting_movie_code = State()
    waiting_movie_file = State()
    waiting_movie_name = State()
    waiting_movie_edit_code = State()
    waiting_movie_edit_name = State()
    waiting_movie_delete_code = State()
    # Channel
    waiting_channel_info = State()
    # Broadcast
    waiting_broadcast_message = State()
    waiting_broadcast_button = State()
    waiting_broadcast_forward = State()
    # Ads
    waiting_ad_content = State()
    waiting_ad_button = State()
    # Text edit
    waiting_text_edit = State()
    # Admin
    waiting_admin_id = State()
    # Top10
    waiting_top10_code = State()
    waiting_top10_name = State()
    # Discussion
    waiting_discussion_url = State()
    # Referral
    waiting_ref_name = State()
    # User search
    waiting_user_search = State()
    # Post
    waiting_post_channel = State()
    waiting_post_content = State()
    # Requests post
    waiting_requests_post = State()

# ============ HELPERS ============
async def is_admin(user_id):
    return await db.is_admin(user_id)

def admin_filter(message_or_callback):
    if isinstance(message_or_callback, Message):
        return message_or_callback.from_user.id in ADMIN_IDS
    return message_or_callback.from_user.id in ADMIN_IDS

# ============ MAIN PANEL ============
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=admin_main_kb())

@router.callback_query(F.data == "admin_main")
async def admin_main_cb(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("🖥 Admin paneliga xush kelibsiz!", reply_markup=admin_main_kb())

# ============ STATISTIKA ============
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    
    bot_info = await callback.bot.get_me()
    total = await db.get_users_count()
    active = await db.get_active_users_count()
    left = await db.get_left_users_count()
    new_24h = await db.get_new_users_count(24)
    new_7d = await db.get_new_users_count(168)
    new_30d = await db.get_new_users_count(720)
    active_24h = await db.get_active_users_in_period(24)
    active_7d = await db.get_active_users_in_period(168)
    active_30d = await db.get_active_users_in_period(720)
    movies_count = await db.get_movies_count()
    downloads = await db.get_downloads_count()

    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Obunachilar soni: <b>{total}</b> ta\n"
        f"✅ Faol obunachilar: <b>{active}</b> ta\n"
        f"❌ Tark etganlar: <b>{left}</b> ta\n\n"
        f"📈 <b>Obunachilar qo'shilishi</b>\n"
        f"• Oxirgi 24 soat: <b>+{new_24h}</b> obunachi\n"
        f"• Oxirgi 7 kun: <b>+{new_7d}</b> obunachi\n"
        f"• Oxirgi 30 kun: <b>+{new_30d}</b> obunachi\n\n"
        f"📊 <b>Faollik</b>\n"
        f"• Oxirgi 24 soatda faol: <b>{active_24h}</b> ta\n"
        f"• Oxirgi 7 kun faol: <b>{active_7d}</b> ta\n"
        f"• Oxirgi 30 kun faol: <b>{active_30d}</b> ta\n\n"
        f"📥 <b>Yuklanishlar</b>\n"
        f"• Jami: <b>{downloads}</b> ta\n\n"
        f"🎬 Kinolar soni: <b>{movies_count}</b> ta\n\n"
        f"🤖 @{bot_info.username}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_admin_kb(), parse_mode="HTML")

# ============ XABAR YUBORISH ============
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "Foydalanuvchilarga yuboradigan xabar turini tanlang.",
        reply_markup=broadcast_type_kb()
    )

@router.callback_query(F.data == "broadcast_normal")
async def broadcast_normal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_broadcast_message)
    await callback.message.edit_text("Foydalanuvchilarga yuboriladigan xabarni yozing:")

@router.message(AdminStates.waiting_broadcast_message)
async def broadcast_message_received(message: Message, state: FSMContext):
    await state.update_data(broadcast_msg=message)
    await state.set_state(None)
    await message.answer(
        "✉️ Xabar yuborishga tayyormisiz?\n\nQuyidagi tugmalar orqali xabarni sozlashingiz yoki yuborishni boshlashingiz mumkin.",
        reply_markup=broadcast_confirm_kb()
    )

@router.callback_query(F.data == "broadcast_send")
async def broadcast_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data.get("broadcast_msg")
    if not msg:
        await callback.answer("Xabar topilmadi!")
        return
    
    users = await db.get_all_users()
    sent = 0
    failed = 0
    
    await callback.message.edit_text("📤 Xabar yuborilmoqda...")
    
    for user in users:
        try:
            await callback.bot.copy_message(
                chat_id=user[1],
                from_chat_id=msg.chat.id,
                message_id=msg.message_id
            )
            sent += 1
        except:
            failed += 1
    
    await callback.message.edit_text(
        f"✅ Xabar yuborildi!\n\n"
        f"✅ Muvaffaqiyatli: {sent} ta\n"
        f"❌ Yuborilmadi: {failed} ta",
        reply_markup=back_to_admin_kb()
    )

@router.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🖥 Admin paneliga xush kelibsiz!", reply_markup=admin_main_kb())

@router.callback_query(F.data == "broadcast_forward")
async def broadcast_forward_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_broadcast_forward)
    await callback.message.edit_text("Boshqa kanaldan xabarni forward qiling:")

@router.message(AdminStates.waiting_broadcast_forward)
async def broadcast_forward_received(message: Message, state: FSMContext):
    await state.update_data(forward_msg=message)
    await state.set_state(None)
    await message.answer(
        "✉️ Xabar yuborishga tayyormisiz?\n\nQuyidagi tugmalar orqali yuborishni boshlashingiz mumkin.",
        reply_markup=forward_confirm_kb()
    )

@router.callback_query(F.data == "broadcast_send_forward")
async def broadcast_send_forward(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data.get("forward_msg")
    if not msg:
        await callback.answer("Xabar topilmadi!")
        return
    
    users = await db.get_all_users()
    sent = 0
    failed = 0
    
    await callback.message.edit_text("📤 Xabar yuborilmoqda...")
    
    for user in users:
        try:
            await callback.bot.forward_message(
                chat_id=user[1],
                from_chat_id=msg.chat.id,
                message_id=msg.message_id
            )
            sent += 1
        except:
            failed += 1
    
    await callback.message.edit_text(
        f"✅ Xabar yuborildi!\n\n"
        f"✅ Muvaffaqiyatli: {sent} ta\n"
        f"❌ Yuborilmadi: {failed} ta",
        reply_markup=back_to_admin_kb()
    )

# ============ KONTENT ============
@router.callback_query(F.data == "admin_content")
async def admin_content(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("🎬 Kontent bo'limiga xush kelibsiz:", reply_markup=admin_content_kb())

# ============ KINOLAR ============
@router.callback_query(F.data == "admin_movies")
async def admin_movies(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("🎬 Kinolar bo'limidasiz:\n\nQuyidagi amallardan birini tanlang:", reply_markup=admin_movies_kb())

@router.callback_query(F.data == "movie_upload")
async def movie_upload_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_movie_code)
    await callback.message.edit_text("🔢 Kino qaysi kodga yuklansin?\n\nKodni kiriting:")

@router.message(AdminStates.waiting_movie_code)
async def movie_code_received(message: Message, state: FSMContext):
    code = message.text.strip()
    existing = await db.get_movie(code)
    if existing:
        await message.answer(f"⚠️ '{code}' kodi allaqachon mavjud! Boshqa kod kiriting:")
        return
    await state.update_data(movie_code=code)
    await state.set_state(AdminStates.waiting_movie_file)
    await message.answer(f"🔢 \"{code}\" kodi qabul qilindi.\n\n🎥 Endi yuklamoqchi bo'lgan kinoni kiriting:")

@router.message(AdminStates.waiting_movie_file, F.video)
async def movie_file_received(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data.get("movie_code")
    await state.update_data(movie_file_id=message.video.file_id)
    await state.set_state(None)
    await message.answer(
        f"🎬 Kino yuklash jarayoni\n\n🔍 Kino kodi: {code}\n\nYuklash turini tanlang:",
        reply_markup=movie_upload_confirm_kb(code)
    )

@router.callback_query(F.data.startswith("movie_save_all_"))
async def movie_save_all(callback: CallbackQuery, state: FSMContext):
    code = callback.data.replace("movie_save_all_", "")
    data = await state.get_data()
    file_id = data.get("movie_file_id")
    await db.add_movie(code, file_id, "", "all")
    await state.clear()
    await callback.message.edit_text(
        f"✅ Kino muvaffaqiyatli saqlandi!\n\n🔍 Kod: {code}\n🔒 Tur: Hammaga",
        reply_markup=admin_movies_kb()
    )

@router.callback_query(F.data.startswith("movie_save_premium_"))
async def movie_save_premium(callback: CallbackQuery, state: FSMContext):
    code = callback.data.replace("movie_save_premium_", "")
    data = await state.get_data()
    file_id = data.get("movie_file_id")
    await db.add_movie(code, file_id, "", "premium")
    await state.clear()
    await callback.message.edit_text(
        f"✅ Kino muvaffaqiyatli saqlandi!\n\n🔍 Kod: {code}\n💎 Tur: Premium",
        reply_markup=admin_movies_kb()
    )

@router.callback_query(F.data.startswith("movie_add_name_"))
async def movie_add_name(callback: CallbackQuery, state: FSMContext):
    code = callback.data.replace("movie_add_name_", "")
    await state.update_data(naming_code=code)
    await state.set_state(AdminStates.waiting_movie_name)
    await callback.message.edit_text("Kino nomini kiriting:")

@router.message(AdminStates.waiting_movie_name)
async def movie_name_received(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data.get("naming_code")
    file_id = data.get("movie_file_id")
    access = data.get("movie_access", "all")
    await db.add_movie(code, file_id, message.text, access)
    await state.clear()
    await message.answer(
        f"✅ Kino saqlandi!\n\n🔍 Kod: {code}\n🎬 Nom: {message.text}",
        reply_markup=admin_movies_kb()
    )

@router.callback_query(F.data == "movie_list")
async def movie_list(callback: CallbackQuery):
    movies = await db.get_all_movies()
    if not movies:
        await callback.message.edit_text(
            "📋 Kinolar ro'yxati\n\n📊 Jami: 0 ta\n\n❌ Kino topilmadi",
            reply_markup=admin_movies_kb()
        )
        return
    
    text = f"📋 Kinolar ro'yxati\n\n📊 Jami: {len(movies)} ta\n\n"
    for i, m in enumerate(movies, 1):
        text += f"{i}. [{m[1]}] {m[3] or 'Nomsiz'} | 👁 {m[5]}\n"
    
    await callback.message.edit_text(text, reply_markup=admin_movies_kb())

@router.callback_query(F.data == "movie_edit")
async def movie_edit_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_movie_edit_code)
    await callback.message.edit_text("📝 Tahrirlamoqchi bo'lgan kino kodini kiriting:")

@router.message(AdminStates.waiting_movie_edit_code)
async def movie_edit_code(message: Message, state: FSMContext):
    code = message.text.strip()
    movie = await db.get_movie(code)
    if not movie:
        await message.answer("❌ Kino topilmadi! Boshqa kod kiriting:")
        return
    await state.update_data(edit_code=code)
    await state.set_state(AdminStates.waiting_movie_edit_name)
    await message.answer_video(
        video=movie[2],
        caption=f"🎬 Kino kodi: {code}\n📝 Hozirgi nomi: {movie[3] or 'Nomsiz'}\n\nYangi nomni kiriting:"
    )

@router.message(AdminStates.waiting_movie_edit_name)
async def movie_edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data.get("edit_code")
    await db.update_movie(code, message.text)
    await state.clear()
    await message.answer(
        f"✅ Kino nomi yangilandi!\n\n🔍 Kod: {code}\n🎬 Yangi nom: {message.text}",
        reply_markup=admin_movies_kb()
    )

@router.callback_query(F.data == "movie_delete")
async def movie_delete_start(callback: CallbackQuery):
    movies = await db.get_all_movies()
    if not movies:
        await callback.message.edit_text("❌ Kinolar yo'q!", reply_markup=admin_movies_kb())
        return
    await callback.message.edit_text(
        "🗑 O'chirish uchun kinoni tanlang:",
        reply_markup=movie_delete_kb(movies)
    )

@router.callback_query(F.data.startswith("movie_del_"))
async def movie_delete_confirm(callback: CallbackQuery):
    code = callback.data.replace("movie_del_", "")
    await db.delete_movie(code)
    await callback.message.edit_text(
        f"✅ Kino o'chirildi! Kod: {code}",
        reply_markup=admin_movies_kb()
    )

# ============ POSTLAR ============
@router.callback_query(F.data == "admin_posts")
async def admin_posts(callback: CallbackQuery):
    await callback.message.edit_text(
        "📬 Postlar bo'limi\n\nKanal yoki guruhga post yuborish uchun quyidagi tugmani bosing.",
        reply_markup=admin_posts_kb()
    )

@router.callback_query(F.data == "post_create")
async def post_create(callback: CallbackQuery):
    await callback.message.edit_text(
        "📢 Kanal yoki guruhni tanlang:\n\nYoki o'zingiz kiriting.",
        reply_markup=post_channel_kb()
    )

@router.callback_query(F.data == "post_enter_channel")
async def post_enter_channel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_post_channel)
    await callback.message.edit_text(
        "✏️ Kanal yoki guruhni kiriting:\n\nQuyidagi usullardan birini tanlang:\n\n"
        "💠 1. Username orqali @kanalUsername\n"
        "💠 2. ID orqali -1001234567890\n"
        "💠 3. Kanaldan xabar forward qilib yuboring"
    )

@router.message(AdminStates.waiting_post_channel)
async def post_channel_received(message: Message, state: FSMContext):
    if message.forward_from_chat:
        channel_id = str(message.forward_from_chat.id)
    else:
        channel_id = message.text.strip()
    
    await state.update_data(post_channel=channel_id)
    await state.set_state(AdminStates.waiting_post_content)
    await message.answer("✅ Kanal tanlandi! Endi post matnini yuboring:")

@router.message(AdminStates.waiting_post_content)
async def post_content_received(message: Message, state: FSMContext):
    data = await state.get_data()
    channel_id = data.get("post_channel")
    try:
        await message.copy_to(chat_id=channel_id)
        await message.answer("✅ Post muvaffaqiyatli yuborildi!", reply_markup=admin_posts_kb())
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)}", reply_markup=admin_posts_kb())
    await state.clear()

# ============ REFERAL ============
@router.callback_query(F.data == "admin_referral")
async def admin_referral(callback: CallbackQuery):
    total = await db.get_total_referrals_count()
    total_users = await db.get_total_referral_users()
    await callback.message.edit_text(
        f"🔗 Referal bo'limi\n\n"
        f"📊 Jami havolalar: {total} ta\n"
        f"👥 Jami kelgan foydalanuvchilar: {total_users} ta",
        reply_markup=admin_referral_kb()
    )

@router.callback_query(F.data == "ref_create")
async def ref_create(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_ref_name)
    await callback.message.edit_text(
        "➕ Referal havola yaratish\n\n"
        "Havola nomini kiriting:\n\n"
        "📌 Namuna:\n"
        "• Instagram\n• Telegram\n• TikTok\n• Do'stlar"
    )

@router.message(AdminStates.waiting_ref_name)
async def ref_name_received(message: Message, state: FSMContext):
    name = message.text.strip()
    code = f"ref_{secrets.token_hex(4)}"
    await db.add_referral(name, code)
    await state.clear()
    
    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={code}"
    
    ref = await db.get_referral_by_code(code)
    await message.answer(
        f"✅ Referal havola yaratildi!\n\n"
        f"📌 Nomi: {name}\n"
        f"🔗 Havola: {link}\n\n"
        f"👥 Kelgan foydalanuvchilar: 0 ta",
        reply_markup=referral_actions_kb(ref[0])
    )

@router.callback_query(F.data == "ref_list")
async def ref_list(callback: CallbackQuery):
    refs = await db.get_all_referrals()
    if not refs:
        await callback.message.edit_text(
            "📋 Referal havolalar ro'yxati\n\n📊 Jami: 0 ta\n\n❌ Havola topilmadi",
            reply_markup=admin_referral_kb()
        )
        return
    
    bot_info = await callback.bot.get_me()
    text = f"📋 Referal havolalar ro'yxati\n📊 Jami: {len(refs)} ta | Sahifa: 1 / 1\n\n"
    
    buttons = []
    for i, ref in enumerate(refs, 1):
        link = f"https://t.me/{bot_info.username}?start={ref[2]}"
        text += f"{i}. {ref[1]}\n👥 Kelganlar: {ref[3]} ta\n🔗 {link}\n📅 {ref[4]}\n\n"
        buttons.append([InlineKeyboardButton(text=f"🔗 {ref[1]} — {ref[3]} ta", callback_data=f"ref_view_{ref[0]}")])
    
    buttons.append([InlineKeyboardButton(text="+ Havola yaratish", callback_data="ref_create")])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_referral")])
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@router.callback_query(F.data.startswith("ref_delete_"))
async def ref_delete(callback: CallbackQuery):
    ref_id = int(callback.data.replace("ref_delete_", ""))
    await db.delete_referral(ref_id)
    await callback.message.edit_text("✅ Havola o'chirildi!", reply_markup=admin_referral_kb())

# ============ KANALLAR ============
@router.callback_query(F.data == "admin_channels")
async def admin_channels(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔑 Majburiy obuna kanallar:",
        reply_markup=admin_channels_kb()
    )

@router.callback_query(F.data == "channel_add")
async def channel_add(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ Majburiy obuna turini tanlang:\n\n"
        "Quyida majburiy obunani qo'shishning 3 ta turi mavjud:\n\n"
        "💠 <b>Ommaviy / Shaxsiy (Kanal · Guruh)</b>\n"
        "Har qanday kanal yoki guruhni majburiy obunaga ulash.\n\n"
        "💠 <b>Shaxsiy / So'rovli havola</b>\n"
        "Shaxsiy yoki so'rovli kanal/guruh havolasi orqali o'tganlarni kuzatish.\n\n"
        "💠 <b>🌐 Oddiy havola</b>\n"
        "Majburiy tekshiruvsiz oddiy havolani ko'rsatish (Instagram, sayt va boshqalar).",
        reply_markup=channel_type_kb(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("ch_type_"))
async def channel_type_selected(callback: CallbackQuery, state: FSMContext):
    ch_type = callback.data.replace("ch_type_", "")
    await state.update_data(channel_type=ch_type)
    await state.set_state(AdminStates.waiting_channel_info)
    
    await callback.message.edit_text(
        "✏️ Kanal yoki guruhni kiriting:\n\n"
        "Quyidagi usullardan birini tanlang:\n\n"
        "💠 1. Username orqali @kanalUsername\n"
        "💠 2. ID orqali -1001234567890\n"
        "💠 3. Kanaldan xabar forward qilib yuboring"
    )

@router.message(AdminStates.waiting_channel_info)
async def channel_info_received(message: Message, state: FSMContext):
    data = await state.get_data()
    ch_type = data.get("channel_type")
    
    if message.forward_from_chat:
        channel_id = str(message.forward_from_chat.id)
        channel_name = message.forward_from_chat.title
        channel_url = f"https://t.me/{message.forward_from_chat.username}" if message.forward_from_chat.username else ""
    else:
        channel_id = message.text.strip()
        try:
            chat = await message.bot.get_chat(channel_id)
            channel_name = chat.title
            channel_url = f"https://t.me/{chat.username}" if chat.username else channel_id
        except:
            channel_name = channel_id
            channel_url = channel_id if channel_id.startswith("http") else ""
    
    if await db.channel_exists(channel_id):
        await message.answer("⚠️ Ushbu Kanal allaqachon qo'shilgan!", reply_markup=admin_channels_kb())
        await state.clear()
        return
    
    await db.add_channel(channel_id, channel_name, ch_type, channel_url)
    await state.clear()
    await message.answer(
        f"✅ Kanal qo'shildi!\n\n📢 Nomi: {channel_name}",
        reply_markup=admin_channels_kb()
    )

@router.callback_query(F.data == "channel_list")
async def channel_list(callback: CallbackQuery):
    channels = await db.get_all_channels()
    if not channels:
        await callback.message.edit_text(
            "⚠️ Majburiy obuna kanallar qo'shilmagan!",
            reply_markup=admin_channels_kb()
        )
        return
    
    text = f"📋 Majburiy obuna kanallari ro'yxati:\n\n📊 Jami: {len(channels)} ta\n\n👆 Kerakli kanal ustiga bosib ma'lumotlarni ko'rishingiz mumkin."
    
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"⚙️ {ch[2]}", callback_data=f"ch_view_{ch[1]}")])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_channels")])
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("ch_view_"))
async def channel_view(callback: CallbackQuery):
    ch_id = callback.data.replace("ch_view_", "")
    channels = await db.get_all_channels()
    ch = next((c for c in channels if c[1] == ch_id), None)
    if not ch:
        await callback.answer("Kanal topilmadi!")
        return
    
    try:
        chat = await callback.bot.get_chat(ch_id)
        member_count = await callback.bot.get_chat_member_count(ch_id)
    except:
        member_count = "?"
    
    text = (
        f"📢 Kanal tafsilotlari\n\n"
        f"📌 Nomi: {ch[2]}\n"
        f"👥 Obunachilar: {member_count}\n"
        f"📅 Qo'shilgan: {ch[5]}"
    )
    
    buttons = []
    if ch[4]:
        buttons.append([InlineKeyboardButton(text="↗️ Kanalga o'tish", url=ch[4])])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="channel_list")])
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data == "channel_delete")
async def channel_delete_start(callback: CallbackQuery):
    channels = await db.get_all_channels()
    if not channels:
        await callback.message.edit_text(
            "⚠️ Majburiy obuna kanallar qo'shilmagan!",
            reply_markup=admin_channels_kb()
        )
        return
    
    await callback.message.edit_text(
        f"📋 Majburiy obuna kanallar ro'yxati:\n\n📊 Jami: {len(channels)} ta\n\n🗑 O'chirish uchun kerakli kanal nomini bosing.",
        reply_markup=channel_delete_kb(channels)
    )

@router.callback_query(F.data.startswith("ch_delete_"))
async def channel_delete_confirm(callback: CallbackQuery):
    ch_id = callback.data.replace("ch_delete_", "")
    await db.delete_channel(ch_id)
    await callback.message.edit_text("✅ Kanal o'chirildi!", reply_markup=admin_channels_kb())

# ============ SOZLAMALAR ============
@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ Tizim sozlamalari bo'limi:",
        reply_markup=admin_settings_kb()
    )

# ============ REKLAMA ============
@router.callback_query(F.data == "settings_ads")
async def settings_ads(callback: CallbackQuery):
    start_status = await db.get_setting("ads_start") or "0"
    movie_status = await db.get_setting("ads_movie") or "0"
    ads_count = await db.get_ads_count()
    active_count = 0
    
    await callback.message.edit_text(
        f"📢 Reklama bo'limi\n\n"
        f"📊 Jami reklamalar: {ads_count} ta\n"
        f"✅ Faol: {active_count} ta\n"
        f"👁 Jami ko'rishlar: 0 ta\n\n"
        f"⚙️ Sozlamalar:\n"
        f"🚀 Start da: {'✅ Yoqiq' if start_status=='1' else '❌ O\'chiq'}\n"
        f"🎬 Kino yuklaganda: {'✅ Yoqiq' if movie_status=='1' else '❌ O\'chiq'}",
        reply_markup=admin_ads_kb(start_status, movie_status)
    )

@router.callback_query(F.data == "ads_toggle_start")
async def ads_toggle_start(callback: CallbackQuery):
    new_val = await db.toggle_ad_setting("start")
    movie_status = await db.get_setting("ads_movie") or "0"
    await callback.message.edit_reply_markup(reply_markup=admin_ads_kb(new_val, movie_status))

@router.callback_query(F.data == "ads_toggle_movie")
async def ads_toggle_movie(callback: CallbackQuery):
    new_val = await db.toggle_ad_setting("movie")
    start_status = await db.get_setting("ads_start") or "0"
    await callback.message.edit_reply_markup(reply_markup=admin_ads_kb(start_status, new_val))

@router.callback_query(F.data == "ads_add")
async def ads_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_ad_content)
    await callback.message.edit_text("➕ Reklama postini yuboring:\n\n📌 Rasm, video yoki matn yuborish mumkin.")

@router.message(AdminStates.waiting_ad_content)
async def ad_content_received(message: Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    else:
        file_id = None
        file_type = "text"
    
    await state.update_data(
        ad_file_id=file_id,
        ad_file_type=file_type,
        ad_caption=message.caption or message.text or "",
        ad_message_id=message.message_id,
        ad_chat_id=message.chat.id
    )
    await state.set_state(None)
    
    await message.answer(
        "👆 Reklama shunday ko'rinadi.\n\nTugma qo'shish yoki saqlashingiz mumkin.",
        reply_markup=ad_confirm_kb()
    )

@router.callback_query(F.data == "ad_save")
async def ad_save(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await db.add_ad(
        data.get("ad_file_id"),
        data.get("ad_file_type"),
        data.get("ad_caption")
    )
    await state.clear()
    await callback.message.edit_text("✅ Reklama saqlandi!", reply_markup=admin_settings_kb())

@router.callback_query(F.data == "ad_cancel")
async def ad_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.", reply_markup=admin_settings_kb())

@router.callback_query(F.data == "ads_list")
async def ads_list(callback: CallbackQuery):
    ads = await db.get_all_ads()
    if not ads:
        await callback.message.edit_text("❌ Reklamalar yo'q!", reply_markup=admin_settings_kb())
        return
    text = f"📋 Reklamalar ro'yxati\n\n📊 Jami: {len(ads)} ta\n"
    await callback.message.edit_text(text, reply_markup=admin_settings_kb())

# ============ ADMINLAR ============
@router.callback_query(F.data == "settings_admins")
async def settings_admins(callback: CallbackQuery):
    await callback.message.edit_text(
        "👮 Adminlar bo'limidasiz:\n\n💠 Bu yerda yangi admin qo'shishingiz yoki mavjudlarini boshqarishingiz mumkin.",
        reply_markup=admin_admins_kb()
    )

@router.callback_query(F.data == "admin_add")
async def admin_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_admin_id)
    await callback.message.edit_text("🆔 Yangi admin ID sini kiriting:")

@router.message(AdminStates.waiting_admin_id)
async def admin_id_received(message: Message, state: FSMContext):
    try:
        admin_id = int(message.text.strip())
        await db.add_admin(admin_id)
        await state.clear()
        await message.answer(f"✅ Admin qo'shildi! ID: {admin_id}", reply_markup=admin_admins_kb())
    except:
        await message.answer("❌ Noto'g'ri ID! Qaytadan kiriting:")

@router.callback_query(F.data == "admin_list")
async def admin_list(callback: CallbackQuery):
    admins = await db.get_all_admins()
    all_admins = list(set(ADMIN_IDS + admins))
    
    if not all_admins:
        await callback.message.edit_text("⚠️ Adminlar qo'shilmagan!", reply_markup=admin_admins_kb())
        return
    
    text = f"👮 Adminlar ro'yxati\n\n📊 Jami: {len(all_admins)} ta\n\n"
    buttons = []
    for admin_id in all_admins:
        text += f"🆔 {admin_id}\n"
        if admin_id not in ADMIN_IDS:
            buttons.append([InlineKeyboardButton(text=f"🗑 {admin_id}", callback_data=f"admin_del_{admin_id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="settings_admins")])
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data == "admin_remove")
async def admin_remove_start(callback: CallbackQuery):
    admins = await db.get_all_admins()
    if not admins:
        await callback.message.edit_text("⚠️ Adminlar qo'shilmagan!", reply_markup=admin_admins_kb())
        return
    
    buttons = []
    for admin_id in admins:
        buttons.append([InlineKeyboardButton(text=f"🗑 {admin_id}", callback_data=f"admin_del_{admin_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="settings_admins")])
    
    await callback.message.edit_text(
        "🗑 O'chirish uchun admin ID sini tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@router.callback_query(F.data.startswith("admin_del_"))
async def admin_delete(callback: CallbackQuery):
    admin_id = int(callback.data.replace("admin_del_", ""))
    await db.remove_admin(admin_id)
    await callback.message.edit_text(f"✅ Admin o'chirildi! ID: {admin_id}", reply_markup=admin_admins_kb())

# ============ MATNLAR ============
TEXT_KEYS = {
    "start": "start_text",
    "channel": "channel_text",
    "subscribe_btn": "subscribe_btn",
    "check_btn": "check_btn",
    "movie_caption": "movie_caption",
    "share_btn": "share_btn",
    "parts_title": "movie_parts_title",
    "wrong_code": "wrong_code_text",
    "part_name": "part_name",
    "movie_name": "movie_name_text",
}

TEXT_DEFAULTS = {
    "start_text": "👋 Assalomu alaykum {name} botimizga xush kelibsiz.\n\n✍🏻 Kino kodini yuboring.",
    "channel_text": "❌ Kechirasiz, botimizdan foydalanish uchun ushbu kanallarga obuna bo'lishingiz kerak.",
    "subscribe_btn": "➕ Obuna bo'lish",
    "check_btn": "✅ Tasdiqlash",
    "movie_caption": "🔍 Kino kodi: {code}\n\n{name}\n\n🤖 Botimiz: @{bot}\n\n👁 Ko'rishlar: {views} ta",
    "share_btn": "↗️ Ulashish",
    "movie_parts_title": "🎬 Kino qismlari ro'yxati:",
    "wrong_code_text": "❌ Kino kodini noto'g'ri yubordingiz!",
    "part_name": "{part}-qism",
    "movie_name_text": "🎬 Nomi:",
}

@router.callback_query(F.data == "settings_texts")
async def settings_texts(callback: CallbackQuery):
    await callback.message.edit_text(
        "📝 Matnlar bo'limi\n\nO'zgartirmoqchi bo'lgan matnni tanlang:",
        reply_markup=admin_texts_kb()
    )

@router.callback_query(F.data.startswith("text_") & ~F.data.startswith("text_reset"))
async def text_edit_start(callback: CallbackQuery, state: FSMContext):
    key_short = callback.data.replace("text_", "")
    db_key = TEXT_KEYS.get(key_short)
    if not db_key:
        return
    
    current = await db.get_setting(db_key)
    
    await state.update_data(editing_text_key=db_key)
    await state.set_state(AdminStates.waiting_text_edit)
    
    format_info = (
        "\n\n✏️ <b>Formatlash:</b>\n"
        "<b>Qalin</b> → &lt;b&gt;Qalin&lt;/b&gt;\n"
        "<i>Kursiv</i> → &lt;i&gt;Kursiv&lt;/i&gt;\n"
        "<u>Tagiga chizilgan</u> → &lt;u&gt;Tagiga chizilgan&lt;/u&gt;\n"
        "<s>O'chirilgan</s> → &lt;s&gt;O'chirilgan&lt;/s&gt;\n"
        "<code>Kod</code> → &lt;code&gt;Kod&lt;/code&gt;"
    )
    
    await callback.message.edit_text(
        f"✏️ <b>Matn tahrirlash</b>\n\n"
        f"📌 Hozirgi matn:\n<blockquote>{current}</blockquote>"
        f"{format_info}\n\n"
        f"📨 Yangi matnni yuboring:",
        reply_markup=text_edit_kb(db_key),
        parse_mode="HTML"
    )

@router.message(AdminStates.waiting_text_edit)
async def text_edit_received(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("editing_text_key")
    await db.set_setting(key, message.text)
    await state.clear()
    await message.answer("✅ Matn yangilandi!", reply_markup=admin_texts_kb())

@router.callback_query(F.data.startswith("text_reset_") & ~F.data.endswith("confirm"))
async def text_reset_single(callback: CallbackQuery):
    key = callback.data.replace("text_reset_", "")
    if key == "all":
        await callback.message.edit_text(
            "⚠️ Barcha matnlarni asliga qaytarishni tasdiqlaysizmi?\n\nBarcha o'zgartirishlar o'chib ketadi!",
            reply_markup=text_reset_confirm_kb()
        )
    else:
        default = TEXT_DEFAULTS.get(key)
        if default:
            await db.set_setting(key, default)
            await callback.message.edit_text("✅ Matn asliga qaytarildi!", reply_markup=admin_texts_kb())

@router.callback_query(F.data == "text_reset_confirm")
async def text_reset_all(callback: CallbackQuery):
    for key, value in TEXT_DEFAULTS.items():
        await db.set_setting(key, value)
    await callback.message.edit_text("✅ Barcha matnlar asliga qaytarildi!", reply_markup=admin_texts_kb())

# ============ SO'ROVLAR ============
@router.callback_query(F.data == "admin_requests")
async def admin_requests(callback: CallbackQuery):
    auto_approve = await db.get_setting("auto_approve") or "0"
    approve_post = await db.get_setting("approve_post") or ""
    post_status = "✅ Belgilangan" if approve_post else "❌ Belgilanmagan"
    
    await callback.message.edit_text(
        f"📩 So'rovlar bo'limi\n\n"
        f"⚡ Avto tasdiqlash: {'✅ Yoqiq' if auto_approve=='1' else '❌ O\'chiq'}\n"
        f"📨 Yuborish posti: {post_status}",
        reply_markup=requests_kb(auto_approve)
    )

@router.callback_query(F.data == "requests_toggle_auto")
async def requests_toggle_auto(callback: CallbackQuery):
    current = await db.get_setting("auto_approve") or "0"
    new_val = "0" if current == "1" else "1"
    await db.set_setting("auto_approve", new_val)
    await callback.message.edit_reply_markup(reply_markup=requests_kb(new_val))

@router.callback_query(F.data == "requests_set_post")
async def requests_set_post(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_requests_post)
    await callback.message.edit_text(
        "📨 Post hali belgilanmagan!\n\n"
        "Foydalanuvchi arizasi tasdiqlanganda unga yuborilishi kerak bo'lgan xabarni (rasm, tekst, video) yuboring:"
    )

@router.message(AdminStates.waiting_requests_post)
async def requests_post_received(message: Message, state: FSMContext):
    await db.set_setting("approve_post", str(message.message_id))
    await state.clear()
    await message.answer("✅ Post belgilandi!", reply_markup=requests_kb("0"))

# ============ FOYDALANUVCHILAR ============
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    total = await db.get_users_count()
    active = await db.get_active_users_count()
    left = await db.get_left_users_count()
    blocked = await db.get_blocked_users_count()
    
    await callback.message.edit_text(
        f"👥 Foydalanuvchilar bo'limi\n\n"
        f"📊 Jami: {total} ta\n"
        f"🟢 Faol: {active} ta\n"
        f"🔴 Tark etgan: {left} ta\n"
        f"🚫 Bloklangan: {blocked} ta",
        reply_markup=admin_users_kb()
    )

@router.callback_query(F.data.startswith("users_list_"))
async def users_list(callback: CallbackQuery):
    page = int(callback.data.replace("users_list_", ""))
    per_page = 10
    users = await db.get_users_page(page, per_page)
    total = await db.get_users_count()
    
    text = f"📋 Foydalanuvchilar ro'yxati\n📊 Jami: {total} ta | Sahifa: {page+1} / {(total+per_page-1)//per_page}\n\n"
    
    buttons = []
    for i, u in enumerate(users, page*per_page+1):
        status = "🟢" if u[5] == 1 else "🔴"
        text += f"{i}. {u[3]} (@{u[2] or 'username_yoq'}) {status}\n🆔 {u[1]} | 📅 {u[8][:10]}\n\n"
        buttons.append([InlineKeyboardButton(
            text=f"{status} {u[3]}", callback_data=f"user_view_{u[1]}"
        )])
    
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"users_list_{page-1}"))
    total_pages = (total+per_page-1)//per_page
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if (page+1)*per_page < total:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"users_list_{page+1}"))
    
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_users")])
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("user_view_"))
async def user_view(callback: CallbackQuery):
    user_id = int(callback.data.replace("user_view_", ""))
    user = await db.search_user(user_id)
    if not user:
        await callback.answer("Foydalanuvchi topilmadi!")
        return
    
    status = "🟢 Faol" if user[5] == 1 else "🔴 Faol emas"
    text = (
        f"👤 Foydalanuvchi ma'lumotlari\n\n"
        f"🆔 ID: {user[1]}\n"
        f"👤 Ismi: {user[3]}\n"
        f"📌 Username: @{user[2] or 'yoq'}\n"
        f"📅 Qo'shilgan: {user[8][:10]}\n"
        f"⚙️ Holat: {status}\n"
        f"🚫 Bloklangan: {'Ha' if user[6]==1 else 'Yo\'q'}"
    )
    await callback.message.edit_text(text, reply_markup=user_actions_kb(user_id))

@router.callback_query(F.data == "users_search")
async def users_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_user_search)
    await callback.message.edit_text("🔎 Foydalanuvchi ID sini kiriting:\n\nMasalan: 123456789")

@router.message(AdminStates.waiting_user_search)
async def user_search_received(message: Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        user = await db.search_user(user_id)
        await state.clear()
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi!", reply_markup=admin_users_kb())
            return
        
        status = "🟢 Faol" if user[5] == 1 else "🔴 Faol emas"
        text = (
            f"👤 Foydalanuvchi ma'lumotlari\n\n"
            f"🆔 ID: {user[1]}\n"
            f"👤 Ismi: {user[3]}\n"
            f"📌 Username: @{user[2] or 'yoq'}\n"
            f"📅 Qo'shilgan: {user[8][:10]}\n"
            f"⚙️ Holat: {status}"
        )
        await message.answer(text, reply_markup=user_actions_kb(user_id))
    except:
        await message.answer("❌ Noto'g'ri ID! Qaytadan kiriting:")

@router.callback_query(F.data.startswith("user_block_"))
async def user_block(callback: CallbackQuery):
    user_id = int(callback.data.replace("user_block_", ""))
    await db.block_user(user_id)
    await callback.message.edit_text(f"🚫 Foydalanuvchi bloklandi! ID: {user_id}", reply_markup=admin_users_kb())

@router.callback_query(F.data.startswith("user_delete_"))
async def user_delete(callback: CallbackQuery):
    user_id = int(callback.data.replace("user_delete_", ""))
    await db.delete_user(user_id)
    await callback.message.edit_text(f"🗑 Foydalanuvchi o'chirildi! ID: {user_id}", reply_markup=admin_users_kb())

@router.callback_query(F.data == "users_blocked")
async def users_blocked(callback: CallbackQuery):
    blocked = await db.get_blocked_users()
    if not blocked:
        await callback.message.edit_text("✅ Bloklangan foydalanuvchilar yo'q.", reply_markup=admin_users_kb())
        return
    
    text = f"🚫 Bloklangan foydalanuvchilar\n\n📊 Jami: {len(blocked)} ta\n\n"
    for u in blocked:
        text += f"🆔 {u[1]} | {u[3]}\n"
    await callback.message.edit_text(text, reply_markup=admin_users_kb())

# ============ TOP 10 ============
@router.callback_query(F.data == "admin_top10")
async def admin_top10(callback: CallbackQuery):
    count = await db.get_top_count()
    await callback.message.edit_text(
        f"🏆 Top 10 boshqaruvi\n\n📊 Jami: {count} ta kino",
        reply_markup=admin_top10_kb()
    )

@router.callback_query(F.data == "top10_add")
async def top10_add(callback: CallbackQuery, state: FSMContext):
    count = await db.get_top_count()
    if count >= 10:
        await callback.answer("Top 10 to'liq! Avval bitta o'chiring.")
        return
    await state.set_state(AdminStates.waiting_top10_code)
    await callback.message.edit_text("🔢 Kino kodini kiriting:")

@router.message(AdminStates.waiting_top10_code)
async def top10_code_received(message: Message, state: FSMContext):
    code = message.text.strip()
    movie = await db.get_movie(code)
    if not movie:
        await message.answer("❌ Bunday kodli kino topilmadi!")
        return
    await db.add_top_movie(code, movie[3] or f"Kino {code}")
    await state.clear()
    await message.answer(f"✅ Top 10 ga qo'shildi!\n\n🎬 Kod: {code}", reply_markup=admin_top10_kb())

@router.callback_query(F.data == "top10_list")
async def top10_list(callback: CallbackQuery):
    movies = await db.get_top_movies()
    if not movies:
        await callback.message.edit_text("❌ Top 10 bo'sh!", reply_markup=admin_top10_kb())
        return
    
    text = "🏆 Top 10 kinolar:\n\n"
    for m in movies:
        text += f"{m[3]}. {m[2]} (kod: {m[1]})\n"
    await callback.message.edit_text(text, reply_markup=admin_top10_kb())

@router.callback_query(F.data == "top10_delete")
async def top10_delete_start(callback: CallbackQuery):
    movies = await db.get_top_movies()
    if not movies:
        await callback.message.edit_text("❌ Top 10 bo'sh!", reply_markup=admin_top10_kb())
        return
    await callback.message.edit_text(
        "🗑 O'chirish uchun kinoni tanlang:",
        reply_markup=top10_delete_kb(movies)
    )

@router.callback_query(F.data.startswith("top10_del_"))
async def top10_delete_confirm(callback: CallbackQuery):
    movie_id = int(callback.data.replace("top10_del_", ""))
    await db.delete_top_movie(movie_id)
    await callback.message.edit_text("✅ Kino top 10 dan o'chirildi!", reply_markup=admin_top10_kb())

# ============ MUHOKAMA ============
@router.callback_query(F.data == "admin_discussion")
async def admin_discussion(callback: CallbackQuery):
    url = await db.get_setting("discussion_url") or ""
    status = f"🔗 {url}" if url else "❌ Belgilanmagan"
    await callback.message.edit_text(
        f"💬 Muhokama boshqaruvi\n\nHozirgi havola: {status}",
        reply_markup=admin_discussion_kb()
    )

@router.callback_query(F.data.in_({"discussion_set", "discussion_edit"}))
async def discussion_set(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_discussion_url)
    await callback.message.edit_text("🔗 Guruh havolasini yuboring:")

@router.message(AdminStates.waiting_discussion_url)
async def discussion_url_received(message: Message, state: FSMContext):
    await db.set_setting("discussion_url", message.text.strip())
    await state.clear()
    await message.answer("✅ Guruh havolasi saqlandi!", reply_markup=admin_discussion_kb())

@router.callback_query(F.data == "discussion_delete")
async def discussion_delete(callback: CallbackQuery):
    await db.set_setting("discussion_url", "")
    await callback.message.edit_text("✅ Havola o'chirildi!", reply_markup=admin_discussion_kb())

@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
