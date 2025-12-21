import traceback
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler, CallbackContext,
)

from telegram.error import BadRequest, TelegramError


from config import REQUESTED_CHANNELS, ADMINS, BANNED, ENG_YAXSHI_VOLONTIYOR_SHEET_NAME, ENG_YAXSHI_TASHABBUSKOR_SHEET_NAME

from sheet.service import  add_voter, is_registreted, get_winnerss, add_volontiyor_or_tashabbuskor

IS_SUB = 0
LANGUAGE = 1
CONTACT = 2
FULLNAME_VOLONTIYOR = 3
COMMENT_VOLONTIYOR = 4
FULLNAME_TASHABBUSKOR = 5
COMMENT_TASHABBUSKOR = 6
GURUH = 7
COMMENT_GURUH = 8
TAVSIYA = 9

async def start(update, context):
    clear_datas(context)

    user_id = update.effective_user.id
    
    if await is_registreted(user_id) or user_id in BANNED:

        await update.message.reply_text("Siz allaqachon ko'nkursda ishtirok etmoqdasiz.\nUshbu buyruqni berish orqali to'plagan ballingizni ko'rishingiz mumkin /myscore!")

        clear_datas(context)
        return ConversationHandler.END


    is_sub = await check_user_in_channels(user_id, context)

    if not is_sub:
        await send_subscribe_message(user_id, context)
        return IS_SUB

    await update.message.reply_text("Xush kelibsiz! 🎉")

    keyboard = [
            [InlineKeyboardButton("English🇺🇸", callback_data="en")],
            [InlineKeyboardButton("O'zbek🇺🇿", callback_data="uz")],
            [InlineKeyboardButton("Русский🇷🇺", callback_data="ru")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Tilni tanlang:", reply_markup=reply_markup)

    return LANGUAGE


async def check_user_in_channels(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    for channel in REQUESTED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except BadRequest:
            return False

    return True


async def send_subscribe_message(user_id, context):
    keyboard = []

    for channel in REQUESTED_CHANNELS:
        keyboard.append([
            InlineKeyboardButton(
                text=channel,
                url=f"https://t.me/{channel}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("Ezgu_uz", url="https://www.instagram.com/volunteers_uz")
    ])

    keyboard.append([
        InlineKeyboardButton("Obuna bo'ldim ✅", callback_data="sub")
    ])

    await context.bot.send_message(
        chat_id=user_id,
        text="Majburiy kanallarga obuna bo'ling:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def catch_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    is_subscribed = await check_user_in_channels(user_id, context)

    if is_subscribed:
        await query.edit_message_text("✅ Obuna tasdiqlandi. Davom etishingiz mumkin.")
        keyboard = [
            [InlineKeyboardButton("English🇺🇸", callback_data="en")],
            [InlineKeyboardButton("O'zbek🇺🇿", callback_data="uz")],
            [InlineKeyboardButton("Русский🇷🇺", callback_data="ru")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("Tilni tanlang:", reply_markup=reply_markup)

        return LANGUAGE
    else:
        await query.answer("❌ Hali barcha kanallarga obuna bo‘lmadingiz", show_alert=True)
        await query.edit_message_text("❌ Hali barcha kanallarga obuna bo‘lmadingiz")
        await send_subscribe_message(user_id, context)
        return IS_SUB
    

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    
    messages = {
        'en': f"Hello, {query.from_user.first_name}! Share your number:",
        'ru': f"Здравствуйте, {query.from_user.first_name}! Поделитесь своим номером:",
        'uz': f"Assalomu alaykum, {query.from_user.first_name}! Raqamingizni ulashing:"
    }

    keyboard = [[KeyboardButton("📞 Share Your Number", request_contact=True)]]
    reply_markup1 = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    
    await query.message.reply_text(text = messages.get(query.data, 'uz'), reply_markup=reply_markup1)
    
    context.user_data['language'] = query.data

    return CONTACT


async def receive_number(update: Update, context: CallbackContext) -> None:
    contact = update.message.contact


    messages = {
        'ru': (
    "📌 <b>ТРЕБОВАНИЯ:</b>\n\n"
    "✅ <b>Указывайте только <i>Фамилия</i> и <i>Имя</i>.</b>❗\n"
    "Фамилия и имя должны быть написаны <b>без орфографических ошибок</b> и <b>латинским алфавитом</b>.\n"
    "Если в имени или фамилии рекомендованного лица есть ошибки, "
    "<b>рекомендация может не учитываться.</b>\n\n"
    "📝 <b>Обратите внимание на комментарий:</b>\n"
    "- Укажите полную и точную информацию о лице\n"
    "- Опишите его деятельность и достижения\n"
    "- При необходимости добавьте ссылки 🔗 и дополнительные материалы 📎\n\n"
    "🙏 <b>Благодарим за понимание и соблюдение требований!</b>"
),
        'en': (
    "📌 <b>REQUIREMENTS:</b>\n\n"
    "✅ <b>Please write only <i>Last Name</i> and <i>First Name</i>.</b>❗\n"
    "The last name and first name must be written <b>without spelling mistakes</b> and <b>using the Latin alphabet</b>.\n"
    "If there are errors in the recommended person’s name or surname, "
    "<b>the recommendation may not be considered.</b>\n\n"
    "📝 <b>Note:</b>\n"
    "- Provide complete and accurate information about the person\n"
    "- Describe their activities and achievements\n"
    "- Include links 🔗 and additional resources 📎 if necessary\n\n"
    "🙏 <b>Thank you for your understanding and cooperation!</b>"
),
        'uz':   (
    "📌 <b>TALABLAR:</b>\n\n"
    "✅ <b>Faqat <i>Familiya</i> va <i>Ism</i> tartibida yozilsin.</b>❗\n"
    "Familiya-ism <b>imloviy xatolarsiz</b> va <b>lotin alifbosida</b> yozilishi shart.\n"
    "Agar tavsiya etilgan shaxsning ismi yoki familiyasida xatolik bo'lsa, "
    "<b>tavsiya hisobga olinmasligi mumkin.</b>\n\n"
    "📝 <b>Izoh qismiga alohida e’tibor bering:</b>\n"
    "- Ushbu shaxs haqida to'liq va aniq ma’lumot bering\n"
    "- Faoliyati va erishgan yutuqlarini yozing\n"
    "- Zarur bo'lsa, havolalar 🔗 va qo'shimcha manbalarni 📎 ilova qiling\n\n"
    "🙏 <b>Tushunishingiz va talablar asosida ma’lumot kiritishingiz uchun rahmat!</b>"
        )
    }
    
    
    context.user_data["contact"] = contact.phone_number
    
    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')), reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")

    messages = {
        'uz': (
    "🏆 *Eng yaxshi “YIL VOLONTYORI-2025” kim munosib deb bilasiz?*\n\n"
    " *Tavsiya:* Familiya va ism (iltimos, to‘liq va tartibli yozing)"
),
        'ru': (
    "🏆 *Кому, по вашему мнению, заслуживает звание «ВОЛОНТЁР ГОДА-2025»?*\n\n"
    "*Рекомендация:* Фамилия и Имя (пожалуйста, пишите полностью и в правильном порядке)"
),
        'en': (
    "🏆 *Who do you think deserves the title “VOLUNTEER OF THE YEAR-2025”?*\n\n"
    "*Recommendation:* Last Name and first Name (please write fully and in correct order)"
)

    }

    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')), reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")

    return FULLNAME_VOLONTIYOR


async def fullname_volontiyor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_fullname = update.message.text

    result = all(not char.isnumeric() for char in user_fullname) and len(user_fullname.split(" ")) != 1

    if not result:
        messages = {
            'uz': f"Siz to'liq ismni noto'g'ri kiritdingiz, \"{user_fullname}\"😕, \nqayta yuboring...",
            'ru': f"Вы неправильно ввели свое полное имя: \"{user_fullname}\"😕, \nотправьте еще раз...",
            'en': f"You have entered full name incorrectly: \"{user_fullname}\"😕, \nsend again..."
        }
        await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')))
        return FULLNAME_VOLONTIYOR


    context.user_data["vol"] = user_fullname

    messages = {
            'uz': 'Izoh bering:',
            'ru': 'Комментарий:',
            'en': 'Comment:'
        }

    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')))
    return COMMENT_VOLONTIYOR


async def comment_volontiyor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    com_vol = update.message.text

    context.user_data["com_vol"] = com_vol

    await add_volontiyor_or_tashabbuskor(context.user_data.get('vol'), user_id, context.user_data.get('com_vol'), ENG_YAXSHI_VOLONTIYOR_SHEET_NAME)

    messages = {
            'uz': (
    "🏆 *Eng yaxshi “YIL TASHABBUSKORI-2025” kim munosib deb bilasiz?*\n\n"
    "*Tavsiya:* Familiya va ism (iltimos, to‘liq va tartibli yozing)"
),
            'ru': (
    "🏆 *Кому, по вашему мнению, заслуживает звание «ТАШАББУСНИК ГОДА-2025»?*\n\n"
    "*Рекомендация:* Фамилия и Имя (пожалуйста, пишите полностью и в правильном порядке)"
),
            'en': (
    "🏆 *Who do you think deserves the title “INITIATOR OF THE YEAR-2025”?*\n\n"
    "*Recommendation:* Last Name and First Name (please write fully and in correct order)"
            )
        }

    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')), parse_mode="Markdown")
    return FULLNAME_TASHABBUSKOR


async def fullname_tashabbuskor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_fullname = update.message.text

    result = all(not char.isnumeric() for char in user_fullname) and len(user_fullname.split(" ")) != 1

    if not result:
        messages = {
            'uz': f"Siz to'liq ismni noto'g'ri kiritdingiz, \"{user_fullname}\"😕, \nqayta yuboring...",
            'ru': f"Вы неправильно ввели полное имя, \"{user_fullname}\"😕, \resend...",
            'en': f"You have entered full name incorrectly: \"{user_fullname}\"😕, \nsend again..."
        }
        await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')))
        return FULLNAME_VOLONTIYOR


    context.user_data["tash"] = user_fullname

    messages = {
            'uz': 'Izoh bering:',
            'ru': 'Комментарий:',
            'en': 'Comment:'
        }

    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')))
    return COMMENT_TASHABBUSKOR


async def comment_tashabbuskor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    com_tash = update.message.text

    context.user_data["com_tash"] = com_tash

    await add_volontiyor_or_tashabbuskor(context.user_data.get('tash'), user_id, context.user_data.get('com_tash'), ENG_YAXSHI_TASHABBUSKOR_SHEET_NAME)

    messages = {
            'uz': (
    "🏆 *ENG YAXSHI VOLONTYORLIK JAMOASI-2025* nominatsiyasiga qaysi jamoa munosib deb bilasiz?\n\n"
    "🔗 (Telegram kanali yoki guruhi linkini yuboring, agar ovozingiz yo‘q bo‘lsa, *no* yoki - deb yozing)"
),
'ru': (
    "🏆 *ЛУЧШАЯ ВОЛОНТЁРСКАЯ КОМАНДА-2025* – какая команда, по вашему мнению, заслуживает этой номинации?\n\n"
    "🔗 (Отправьте ссылку на канал или группу в Telegram, если не хотите голосовать, напишите *нет*)"
),
'en': (
    "🏆 *BEST VOLUNTEER TEAM-2025* – which team do you think deserves this nomination?\n\n"
    "🔗 (Send the Telegram channel or group link, if you don’t want to vote, type *no*)"
)


        }

    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')), parse_mode="Markdown")
    await add_voter(user_id, context.user_data.get('contact'), context.user_data.get('guruh', '-'), context.user_data.get('tavsiya', '-'))
    return GURUH

async def guruh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guruh_link = update.message.text

    if guruh_link.lower() not in ['нет', 'no', '-']:
        context.user_data["guruh"] = guruh_link

    messages = {
            'uz': (
                "💡 *2026 yil uchun Volontyorlik faoliyatida qanday tavsiyalaringiz bor?*\n\n"
                "✏️ Iltimos, fikringizni qisqacha yozing, , agar ovozingiz yo‘q bo‘lsa, *no* yoki - deb yozing"
            ),
            'ru': (
                "💡 *Какие у вас есть рекомендации по волонтерской деятельности на 2026 год?*\n\n"
                "✏️ Пожалуйста, напишите свой ответ коротко, если не хотите голосовать, напишите *нет*"
            ),
            'en': (
                "💡 *What are your recommendations for volunteering activities in 2026?*\n\n"
                "✏️ Please, write your thoughts briefly, if you don’t want to vote, type *no*"
            ) }

    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')), parse_mode="Markdown")
    return TAVSIYA

async def tavsiya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_tavsiya = update.message.text

    if user_tavsiya.lower() not in ['нет', 'no', '-']:
        context.user_data["tavsiya"] = user_tavsiya

    messages = {
            'uz': (
    "🌟 Ishtirokingiz uchun tashakkur!\n"
    "💬 Sizing fikringiz biz uchun muhim.\n"
    "✅ So‘rov qabul qilindi"
),
'ru': (
    "🌟 Спасибо за ваше участие!\n"
    "💬 Ваше мнение важно для нас.\n"
    "✅ Опрос принят"
),
'en': (
    "🌟 Thank you for your participation!\n"
    "💬 Your opinion is important to us.\n"
    "✅ Survey received"
)
 }

    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')), parse_mode="Markdown")

    await add_voter(user_id, context.user_data.get('contact'), context.user_data.get('guruh', '-'), context.user_data.get('tavsiya', '-'))

    clear_datas(context)
    return ConversationHandler.END




async def eng_yaxshi_volontiyorlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    winners = await get_winnerss(ENG_YAXSHI_VOLONTIYOR_SHEET_NAME)

    t = 1
    text = "📌 *Eng yaxshi volontiyorlar* 🥳\n\n"
    for w in winners:
        text = text + (
            f"{t}) 👤: {w[0]} {w[1]} 🅱️: {w[2]}\n"
        )
            
        t = t + 1
    await context.bot.send_message(chat_id=update.effective_user.id, text= text, parse_mode="Markdown")
        
    clear_datas(context)
    return ConversationHandler.END


async def eng_yaxshi_tashabbuskorlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    winners = await get_winnerss(ENG_YAXSHI_TASHABBUSKOR_SHEET_NAME)

    t = 1
    text = "📌 *Eng yaxshi tashabbuskorlar* 🥳\n\n"
    for w in winners:
        text = text + (
            f"{t}) 👤: {w[0]} {w[1]} 🅱️: {w[2]}\n"
        )
            
        t = t + 1
    await context.bot.send_message(chat_id=update.effective_user.id, text= text, parse_mode="Markdown")
        
    clear_datas(context)
    return ConversationHandler.END


async def send_messagee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMINS[0]:
    
        text = update.message.text

        words = text.split(" ", 2)

        try:
            await context.bot.send_message(chat_id=words[1], text=words[2])
            await context.bot.send_message(chat_id=update.effective_user.id, text="Yuborildi✅")
        except TelegramError as e:
            await context.bot.send_message(chat_id=update.effective_user.id, text="Yuborilmadi ❌\n" + e.message)
        
    else:
        await context.bot.send_message(chat_id=update.effective_user.id, text="Bu buyruq siz uchun emas🙈😊")
    
    clear_datas(context)
    return ConversationHandler.END


def clear_datas(context):
    context.chat_data.clear()
    context.user_data.clear()


async def error_handler(update: Update, context: CallbackContext):
    # NoneType chat_id xatosini e’tiborsiz qoldirish
    if context.error and "'NoneType' object has no attribute 'chat_id'" in str(context.error):
        return

    # To‘liq traceback olish
    tb = "".join(
        traceback.format_exception(
            type(context.error),
            context.error,
            context.error.__traceback__
        )
    )

    error_text = (
        "🚨 *Botda xatolik yuz berdi!*\n\n"
        f"*Xato turi:* `{type(context.error).__name__}`\n\n"
        f"*Xato matni:*\n`{context.error}`\n\n"
        f"*Qayerda (traceback):*\n```{tb}```"
    )

    await context.bot.send_message(
        chat_id=ADMINS[0],
        text=error_text,
        parse_mode="Markdown"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    messages = {
        'uz': 'Bekor qilindi!',
        'ru': 'Отменено!',
        'en': 'Cancelled!'
    }
    await update.message.reply_text(messages.get(context.user_data.get('language'), messages.get('uz')))
    await add_voter(update.effective_user.id, context.user_data.get('contact','-'), context.user_data.get('guruh', '-'), context.user_data.get('tavsiya', '-'))
    clear_datas(context)
    return ConversationHandler.END


