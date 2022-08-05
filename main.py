from config import *  # se importa el token e IDs
from amz import AmzScraper
import telebot  # Para importar la API de Telegram
from telebot.types import InlineKeyboardMarkup # Para crear menu de botones
from telebot.types import InlineKeyboardButton # Para definir botones inline
import re # Para evaluar expresiones regulares

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

@bot.callback_query_handler(func=lambda x: True)
def respuesta_botones(call): # Gestiona las acciones del menu de botones
    chat_id = call.from_user.id
    message_id = call.message.id
    if call.data == "stock":
        bot.send_message(chat_id, "Introduce la URL del producto que deseas rastrear: ")
    if call.data == "precio":
        bot.send_message(chat_id, "Mensaje de rastreo de precio")
    if call.data == "delete":
        bot.send_message(chat_id, "Lista de los productos en rastreo")
    if call.data == "help":
        msg_help = f'🆘 <b>Ayuda</b> 🆘 \n\n' \
                   f'<b>🔶 ¿Qué es Trackmazon?</b> \n' \
                   f'   🔹 Trackmazon es un asistente que te ayuda a encontrar las mejores ofertas de productos de Amazon, ' \
                   f'avisándote cuando un producto vuelva a tener stock o haya bajado su precio. \n\n' \
                   f'<b>🔶 ¿Como funciona Trackmazon?</b> \n' \
                   f'🔹 Puedes escoger entre 2 opciones: \n     <b>1.</b> Rastrear un producto que no está en stock. Trackmazon te avisará' \
                   f' cuando ese producto vuelva a estar disponible.\n     <b>2.</b> Rastrear el precio de un producto. Trackmazon te avisará' \
                   f' cuando el precio de un producto esté por debajo del precio que has indicado.\n\n' \
                   f'<b>🔶 ¿Qué hago si quiero dejar de rastrear un producto?</b> \n' \
                   f'🔹 En el menú principal (cuando escribes el comando /start) existe una opción "Eliminar rastreo" que' \
                   f' listará todos los productos que están siendo rastreados y podrás elegir uno para dejar de rastrearlo. \n'

        bot.send_message(chat_id, msg_help, parse_mode="html")

# Responde a los mensajes que contienen una URL de Amazon
# Empleamos una regexp que indentifica URLs de Amazon
# https://regex101.com/r/UaxDyp/1
# ^([https?://www\.]*amazon\.(com|es|co\.uk|de|fr|it|nl)).*?(\/[dg]p\/[^/]+).*
@bot.message_handler(regexp=AMZ_REGEXP)
# Gestiona los mensajes con enlaces de amazon
def handle_url(message):
    bot.reply_to(message, "La url introducida es correcta")
    amz = AmzScraper(message.text) # Instanciamos la clase
    output = amz.getProductPrize() # Pasamos la url al metodo
    bot.send_message(message.chat.id, output)

# Responde a los comandos /stock y /precio
@bot.message_handler(commands=["stock", "precio"])
def cmd_reply(message):
    bot.send_message(message.chat.id, "Introduce la URL del producto que deseas rastrear: ")

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
