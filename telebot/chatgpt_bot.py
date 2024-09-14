import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters, ConversationHandler, CallbackQueryHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
WELCOME, MAIN_MENU, CHOOSE_SERVICE, CHOOSE_DOCTOR, SELECT_DATE, CONFIRMATION = range(6)

# Define the start command handler
async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [[InlineKeyboardButton("Press M", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to Tenama Digital Solution! Please press 'M' to display the menu.",
        reply_markup=reply_markup
    )
    return WELCOME

# Handle menu selection
async def menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("1. Consultancy", callback_data='consultancy')],
        [InlineKeyboardButton("2. Ambulance", callback_data='ambulance')],
        [InlineKeyboardButton("3. Pharmacy", callback_data='pharmacy')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Please choose an option:", reply_markup=reply_markup)
    return MAIN_MENU

# Handle service choice
async def service_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    service = query.data
    if service == 'consultancy':
        keyboard = [
            [InlineKeyboardButton("1. Dr. Amanuel", callback_data='dr_amanuel')],
            [InlineKeyboardButton("2. Dr. Solomon", callback_data='dr_solomon')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Choose a doctor:", reply_markup=reply_markup)
        return CHOOSE_DOCTOR
    elif service == 'ambulance':
        await query.edit_message_text(text="Ambulance service is not implemented yet.")
        return ConversationHandler.END
    elif service == 'pharmacy':
        await query.edit_message_text(text="Pharmacy service is not implemented yet.")
        return ConversationHandler.END

# Handle doctor choice
async def choose_doctor(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    doctor = query.data
    context.user_data['doctor'] = doctor
    # Example dates for selection
    keyboard = [
        [InlineKeyboardButton("2024-09-15", callback_data='2024-09-15')],
        [InlineKeyboardButton("2024-09-16", callback_data='2024-09-16')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Select a date:", reply_markup=reply_markup)
    return SELECT_DATE

# Handle date selection
async def select_date(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    date = query.data
    context.user_data['date'] = date
    doctor = context.user_data.get('doctor')
    await query.edit_message_text(
        text=f"Doctor: {doctor}\nDate: {date}\n\nPlease confirm your appointment.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Confirm", callback_data='confirm')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')]
        ])
    )
    return CONFIRMATION

# Handle confirmation
async def confirmation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == 'confirm':
        doctor = context.user_data.get('doctor')
        date = context.user_data.get('date')
        await query.edit_message_text(text=f"Appointment confirmed with {doctor} on {date}.")
    else:
        await query.edit_message_text(text="Appointment cancelled.")
    return ConversationHandler.END

# Error handler
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

def main() -> None:
    TOKEN = "7233846991:AAEy0fp_d4zzTVQfD0MflnYwTgU9Cq5f5KM"

    application = Application.builder().token(TOKEN).build()

    # Define conversation handler with states
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME: [CallbackQueryHandler(menu, pattern='menu')],
            MAIN_MENU: [CallbackQueryHandler(service_choice)],
            CHOOSE_DOCTOR: [CallbackQueryHandler(choose_doctor)],
            SELECT_DATE: [CallbackQueryHandler(select_date)],
            CONFIRMATION: [CallbackQueryHandler(confirmation)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    # Register handlers
    application.add_handler(conversation_handler)
    application.add_error_handler(error)

    application.run_polling()

if __name__ == '__main__':
    main()
