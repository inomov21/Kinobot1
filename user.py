from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from keyboards import *

router = Router()

class UserStates(StatesGroup):
    waiting_search_code = State()

# ============ HELPERS ============
async def check_subscription(bot, user_id):
    channels = await db.get_all_channels()
    if not channels:
        return True
    
    for ch in channels:
        ch_id = ch[1]
        ch_type = ch[3]
        
        if ch_type == "link":
            continue
        
        try:
            member = await bot.get_chat_member(ch_id, user_id)
            if member.status in ["left", "kicked", "banned"]:
                return False
        except:
            pass
    
    return True

async def send_movie(message_or_callback, code, bot):
    movie = await db.get_movie(code)
    
    if isinstance(message_or_callback, CallbackQuery):
        user = message_or_callback.from_user
        send = message_or_callback.message
    else:
        user = message_or_callback.from_user
        send = message_or_callback

    if not movie:
        wrong_code = await db.get_setting("wrong_code_text")
        await send.answer(wrong_code)
        return

    await db.increment_views(code)
    
    bot_info = await bot.get_me()
    caption_template = await db.get_setting("movie_caption")
    share_btn_text = await db.get_setting("share_btn")
    
    caption = caption_template.format(
        code=movie[1],
        name=movie[3] or "",
        bot=bot_info.username,
        views=movie[5] + 1
    )

    share_kb = movie_share_kb(code, bot_info.username, share_btn_text)

    # Reklama ko'rsatish
    movie_ads_on = await db.get_setting("ads_movie") or "0"
    if movie_ads_on == "1":
        ads = await db.get_all_ads()
        if ads:
            ad = ads[0]
            try:
                if ad[2] == "photo":
                    await send.answer_photo(photo=ad[1], caption=ad[3])
                elif ad[2] == "video":
                    await send.answer_video(video=ad[1], caption=ad[3])
                else:
                    await send.answer(ad[3])
            except:
                pass

    await send.answer_video(
        video=movie[2],
        caption=caption,
        reply_markup=share_kb,
        parse_mode="HTML"
    )

# ============ START ============
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    args = message.text.split()
    ref_code = args[1] if len(args) > 1 else None

    existing = await db.get_user(user.id)
    await db.add_user(user.id, user.username, user.full_name, ref_code)
    await db.update_last_active(user.id)

    # Referal hisoblash
    if ref_code and ref_code.startswith("ref_") and not existing:
        ref = await db.get_referral_by_code(ref_code)
        if ref:
            await db.add_referral_user(ref[0], user.id)
    
    # Kino kodi bilan kelgan bo'lsa
    movie_code = None
    if ref_code and not ref_code.startswith("ref_"):
        movie_code = ref_code

    # Majburiy obuna tekshirish
    is_subscribed = await check_subscription(message.bot, user.id)
    if not is_subscribed:
        channels = await db.get_all_channels()
        channel_text = await db.get_setting("channel_text")
        kb = subscribe_kb(channels, "")
        await message.answer(channel_text, reply_markup=kb)
        if movie_code:
            await db.set_setting(f"pending_movie_{user.id}", movie_code)
        return

    # Reklama ko'rsatish
    start_ads_on = await db.get_setting("ads_start") or "0"
    if start_ads_on == "1":
        ads = await db.get_all_ads()
        if ads:
            ad = ads[0]
            try:
                if ad[2] == "photo":
                    await message.answer_photo(photo=ad[1], caption=ad[3])
                elif ad[2] == "video":
                    await message.answer_video(video=ad[1], caption=ad[3])
                else:
                    await message.answer(ad[3])
            except:
                pass

    start_text = await db.get_setting("start_text")
    text = start_text.format(name=user.full_name)
    await message.answer(text, reply_markup=user_main_kb())

    # Agar kino kodi bilan kelgan bo'lsa
    if movie_code:
        await send_movie(message, movie_code, message.bot)

# ============ OBUNA TEKSHIRISH ============
@router.callback_query(F.data == "check_subscribe")
async def check_subscribe(callback: CallbackQuery):
    user = callback.from_user
    is_subscribed = await check_subscription(callback.bot, user.id)
    
    if not is_subscribed:
        await callback.answer("❌ Siz hali barcha kanallarga obuna bo'lmagansiz!", show_alert=True)
        return
    
    await callback.message.delete()
    
    start_text = await db.get_setting("start_text")
    text = start_text.format(name=user.full_name)
    await callback.message.answer(text, reply_markup=user_main_kb())

    # Kutayotgan kino
    pending = await db.get_setting(f"pending_movie_{user.id}")
    if pending:
        await send_movie(callback.message, pending, callback.bot)
        await db.set_setting(f"pending_movie_{user.id}", "")

# ============ KINO KODI ============
@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message, state: FSMContext):
    user = message.from_user
    text = message.text.strip()
    
    await db.update_last_active(user.id)
    
    # Majburiy obuna tekshirish
    is_subscribed = await check_subscription(message.bot, user.id)
    if not is_subscribed:
        channels = await db.get_all_channels()
        channel_text = await db.get_setting("channel_text")
        kb = subscribe_kb(channels, "")
        await message.answer(channel_text, reply_markup=kb)
        return

    # Tugmalar
    if text == "🔍 Qidiruv":
        await state.set_state(UserStates.waiting_search_code)
        await message.answer(
            "🔍 Iltimos kino kodini yozing:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")]
            ])
        )
        return
    
    if text == "🏆 Top 10":
        movies = await db.get_top_movies()
        if not movies:
            await message.answer("❌ Top 10 hali to'ldirilmagan!")
            return
        
        top_text = "🏆 <b>Top 10 kinolar</b>\n\n"
        for m in movies:
            top_text += f"{m[3]}. {m[2]} — kod: <code>{m[1]}</code>\n"
        await message.answer(top_text, parse_mode="HTML")
        return
    
    if text == "💬 Muhokama":
        url = await db.get_setting("discussion_url") or ""
        if not url:
            await message.answer("❌ Muhokama guruhi hali belgilanmagan!")
            return
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Guruhga o'tish", url=url)]
        ])
        await message.answer("💬 Muhokama guruhimizga xush kelibsiz!", reply_markup=kb)
        return
    
    if text == "📢 Reklama":
        bot_info = await message.bot.get_me()
        await message.answer(
            f"👋 Assalomu alaykum, {user.full_name}!\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📣 Reklama uchun:\n"
            f"👤 @inomov21\n\n"
            f"👨‍💻 Yaratuvchi:\n"
            f"👤 @inomov21\n"
            f"━━━━━━━━━━━━━━━"
        )
        return
    
    if text == "🔗 Referal":
        bot_info = await message.bot.get_me()
        ref_code = f"user_{user.id}"
        link = f"https://t.me/{bot_info.username}?start={ref_code}"
        ref_count = await db.get_user_referral_count(ref_code)
        
        await message.answer(
            f"👋 Assalomu alaykum, {user.full_name}!\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 Sizning referal havolangiz:\n"
            f"{link}\n\n"
            f"👥 Taklif qilganlar: {ref_count} ta\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🎁 MAXSUS TAKLIF!\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👫 10 ta do'stingizni taklif qiling\n"
            f"💸 5,000 so'm PAYNET orqali\n"
            f"    telefon raqamingizga o'tkazamiz!\n\n"
            f"📩 Murojaat uchun:\n"
            f"👤 Admin: @inomov21\n"
            f"━━━━━━━━━━━━━━━"
        )
        return

    # Kino kodi
    await send_movie(message, text, message.bot)

# ============ QIDIRUV ============
@router.message(UserStates.waiting_search_code)
async def search_code_received(message: Message, state: FSMContext):
    await state.clear()
    code = message.text.strip()
    await send_movie(message, code, message.bot)

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = callback.from_user
    start_text = await db.get_setting("start_text")
    text = start_text.format(name=user.full_name)
    await callback.message.edit_text(text)
    await callback.message.answer("Asosiy menyu:", reply_markup=user_main_kb())
