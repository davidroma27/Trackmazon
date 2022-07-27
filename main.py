from config import *  # se importa el token e IDs
import telebot  # Para importar la API de Telegram
from telebot.types import InlineKeyboardMarkup # Para crear menu de botones
from telebot.types import InlineKeyboardButton # Para definir botones inline

# instacia del bot
bot = telebot.TeleBot(TLG_TOKEN)  # Le pasamos el token del bot a instanciar


# respuesta al comando /start
@bot.message_handler(commands=["start"])  # Se establece un decorador que responderá al comando /start
def cmd_start(message):
    markup = InlineKeyboardMarkup(row_width=1) # Establecemos un boton por fila (3 por defecto)
    b_stock = InlineKeyboardButton("Rastrear stock 📈", callback_data="stock")
    b_precio = InlineKeyboardButton("Rastrear precio 💸", callback_data="precio")
    b_delete = InlineKeyboardButton("Eliminar rastreo ❌", callback_data="delete")
    b_help = InlineKeyboardButton("Ayuda 🆘", callback_data="help")
    markup.add(b_stock,b_precio,b_delete,b_help) # Agregamos los botones al markup
    bot.send_message(message.chat.id, "👋 Bienvenido a Trackmazon! 👋 \n Para empezar elige una opción del menú 👇",
                     reply_markup=markup)




# Responde a los mensajes de texto que no son comandos
@bot.message_handler(content_types=["text"])
# Gestiona mensajes de texto
def text_messages(message):
    if message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no disponible")



# --- MAIN ---
if __name__ == "__main__":
    print('Iniciando el bot')
    bot.infinity_polling()  # Permanece a la escucha de nuevos mensajes
    print('Fin')
