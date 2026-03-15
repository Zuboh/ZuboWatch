from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_keyboard(options: list[str], selected: list[str], columns: int = 2) -> InlineKeyboardMarkup:
    keyboard = []
    row = []

    for i, option in enumerate(options, 1):
        text = f"✅ {option}" if option in selected else option
        row.append(InlineKeyboardButton(text, callback_data=option))
        if i % columns == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)