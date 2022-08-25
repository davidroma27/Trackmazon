from config import *  # se importa el token e IDs
from amz import *
import telebot  # Para importar la API de Telegram
from telebot.async_telebot import AsyncTeleBot
import asyncio
import aiohttp
from telebot.types import InlineKeyboardMarkup  # Para crear menu de botones
from telebot.types import InlineKeyboardButton  # Para definir botones inline
from multiprocessing import freeze_support
from dbhelper import DBHelper
import re  # Para evaluar expresiones regulares

# instacia del bot
bot = AsyncTeleBot(TLG_TOKEN)  # Le pasamos el token del bot a instanciar
db = DBHelper()  # Instancia de la base de datos


# respuesta al comando /start
@bot.message_handler(commands=["start"])  # Se establece un decorador que responderá al comando /start
async def start(message):
    await bot.send_message(message.chat.id,
                           "👋 Bienvenido a Trackmazon! 👋 \n Para empezar introduce la URL de un producto")
# async def cmd_start(message):
#     markup = InlineKeyboardMarkup(row_width=1)  # Establecemos un boton por fila (3 por defecto)
#     b_stock = InlineKeyboardButton("Rastrear stock 📈", callback_data="stock")
#     b_precio = InlineKeyboardButton("Rastrear precio 💸", callback_data="precio")
#     b_delete = InlineKeyboardButton("Eliminar rastreo ❌", callback_data="delete")
#     b_help = InlineKeyboardButton("Ayuda 🆘", callback_data="help")
#     markup.add(b_stock, b_precio, b_delete, b_help)  # Agregamos los botones al markup
#     await bot.send_message(message.chat.id,
#                            "👋 Bienvenido a Trackmazon! 👋 \n Para empezar elige una opción del menú 👇",
#                            reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: True)
# async def respuesta_botones(call):  # Gestiona las acciones del menu de botones
#     chat_id = call.from_user.id
#     message_id = call.message.id
#     action = call.data
#     if call.data == "stock":
#         action = 'stock'
#         await bot.send_message(chat_id, f'Has elegido rastrear {action}')
#         # bot.register_next_step_handler(msg, process_stock_step)
#     if call.data == "precio":
#         action = 'precio'
#         await bot.send_message(chat_id, f"Has elegido rastrear {action}")
#         # bot.register_next(chat_id, "Introduce la URL del producto que deseas rastrear el precio: ")
#         # bot.register_next_step_handler(msg, process_prize_step)
#     if call.data == "delete":
#         await bot.send_message(chat_id, "Lista de los productos en rastreo")
#     if call.data == "help":
#         msg_help = f'🆘 <b>Ayuda</b> 🆘 \n\n' \
#                    f'<b>🔶 ¿Qué es Trackmazon?</b> \n' \
#                    f'   🔹 Trackmazon es un asistente que te ayuda a encontrar las mejores ofertas de productos de Amazon, ' \
#                    f'avisándote cuando un producto vuelva a tener stock o haya bajado su precio. \n\n' \
#                    f'<b>🔶 ¿Como funciona Trackmazon?</b> \n' \
#                    f'🔹 Puedes escoger entre 2 opciones: \n     <b>1.</b> Rastrear un producto que no está en stock. Trackmazon te avisará' \
#                    f' cuando ese producto vuelva a estar disponible.\n     <b>2.</b> Rastrear el precio de un producto. Trackmazon te avisará' \
#                    f' cuando el precio de un producto esté por debajo del precio que has indicado.\n\n' \
#                    f'<b>🔶 ¿Qué hago si quiero dejar de rastrear un producto?</b> \n' \
#                    f'🔹 En el menú principal (cuando escribes el comando /start) existe una opción "Eliminar rastreo" que' \
#                    f' listará todos los productos que están siendo rastreados y podrás elegir uno para dejar de rastrearlo. \n'
#
#         await bot.send_message(chat_id, msg_help, parse_mode="html")


# # Responde al comando /stock
# @bot.message_handler(commands=["stock"])
# async def getData(message):
#     msg = bot.send_message(message.chat.id, "Introduce la URL del producto que deseas rastrear: ")
#     bot.register_next_step_handler(msg, process_stock_step)
#
# # Responde al comando /precio
# @bot.message_handler(commands=["precio"])
# def getData(message):
#     msg = bot.send_message(message.chat.id, "Introduce la URL del producto que deseas rastrear: ")
#     bot.register_next_step_handler(msg, process_prize_step)


# Responde a los mensajes que contienen una URL de Amazon
# Empleamos una regexp que indentifica URLs de Amazon
# https://regex101.com/r/UaxDyp/1
# ^([https?://www\.]*amazon\.(com|es|co\.uk|de|fr|it|nl)).*?(\/[dg]p\/[^/]+).*
@bot.message_handler(regexp=AMZ_REGEXP)
# Gestiona los mensajes con enlaces de amazon
async def handle_url(message):
    global url
    global urlMsg
    urlMsg = message
    url = message.text
    await bot.reply_to(message, "La url introducida es correcta")

    markup = InlineKeyboardMarkup(row_width=1)  # Establecemos un boton por fila (3 por defecto)
    b_stock = InlineKeyboardButton("Rastrear stock 📈", callback_data="stock")
    b_precio = InlineKeyboardButton("Rastrear precio 💸", callback_data="precio")
    markup.add(b_stock, b_precio)  # Agregamos los botones al markup
    await bot.send_message(message.chat.id, "Elige la opción que quieres rastrear: ",
                           reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'stock' or call.data == 'precio')
async def respuesta_botones(call):  # Gestiona las acciones del menu de botones
    chat_id = call.from_user.id
    message_id = call.message.id

    if call.data == 'stock':
        try:
            # Obtenemos los datos de Amazon
            await bot.send_message(chat_id, "Obteniendo stock...")
            amz = AmzScraper()
            stock = await amz.main(url, 'stock')  # Realiza el scraping para stock

            # Si el stock devuelve vacío muestra que no esta disponible
            if stock[1] == '':
                await bot.send_message(chat_id, f'Estado actual: No disponible.')
            else: # Si no, muestra el estado del stock que muestra en la web
                await bot.send_message(chat_id, f'Estado actual: {stock[1]}')

            # Si no hay stock realiza el rastreo. Si hay stock no hace nada
            if stock[1] == '' or stock[1] == 'No disponible.':
                db.add_tracking(chat_id, url, stock[0], 'stock', stock[1])  # Se almacena en la base de datos el nuevo rastreo
                await bot.send_message(chat_id, f'<b> Rastreando stock </b> ✅\n '
                                            f'🔷 {stock[0]}\n', parse_mode="html")
            else: # Si el producto ya se encuentra en stock no se rastrea
                await bot.send_message(chat_id, f'Este producto ya se ecuentra en stock! Prueba a rastrear su precio 😉')

        except Exception as e:
            await bot.reply_to(call.message, "Se ha producido un error durante el rastreo 😢")
            # await bot.send_message(chat_id, str(e))

    if call.data == 'precio':
        global precio
        try:
            # Obtenemos los datos de Amazon
            await bot.send_message(chat_id, "Obteniendo precio...")
            amz = AmzScraper()
            stock = await amz.main(url, 'stock')  # Comprobamos que el producto esta disponible

            # Si el stock devuelve vacío muestra que no esta disponible
            if stock[1] == '':
                await bot.send_message(chat_id, f'Estado actual: No disponible.')
            else: # Si no, muestra el estado del stock que muestra en la web
                await bot.send_message(chat_id, f'Estado actual: {stock[1]}')

            # Si no hay stock no realiza rastreo de precio
            if stock[1] == '' or stock[1] == 'No disponible.':
                await bot.reply_to(urlMsg, f'El producto no tiene stock, imposible rastrear precio. Prueba a rastrear el stock! 😉')
            else:
                # Si hay stock rastrea el precio y lo almacena
                precio = await amz.main(url, 'precio')  # Realiza el scraping para precio
                db.add_tracking(chat_id, url, precio[0], 'precio', precio[1])  # Se almacena en la base de datos el nuevo rastreo
                await bot.send_message(chat_id, f'<b> Rastreando precio </b> ✅\n '
                                                f'🔷 {precio[0]}\n'
                                                f'🔸 Precio actual: {precio[1]}\n', parse_mode="html")
        except Exception as e:
            # await bot.reply_to(call.message, str(e))
            await bot.reply_to(call.message, "Se ha producido un error durante el rastreo 😢")

# respuesta al comando /list
@bot.message_handler(commands=["list"])  # Se establece un decorador que responderá al comando /list
async def list_products(message):
    global lista
    lista = db.get_trackings(message.chat.id)  # Obtiene de la BD los productos del usuario
    n_items = len(lista)
    msg = f'<b>Estás rastreando {n_items} productos</b>\n\n'

    teclado = InlineKeyboardMarkup(row_width=3)

    for e in lista:
        msg += f'🔹 [{lista.index(e)}] - {e}\n'
        teclado.add(InlineKeyboardButton(f'[{lista.index(e)}]', callback_data=f'{lista.index(e)}'))

    if len(lista) > 0:
        msg += f'\nPuedes seleccionar debajo un producto para eliminar 👇'

    await bot.send_message(message.chat.id, msg, parse_mode="html", reply_markup=teclado)


@bot.callback_query_handler(func=lambda call: True)
async def eliminar_producto(req):
    chat_id = req.from_user.id
    titulo = lista[int(req.data)]
    producto = db.get_url(titulo).pop()[0]
    try:
        db.del_tracking(producto, chat_id)
        await bot.send_message(chat_id, f"El producto ha sido eliminado ✅")
    except Exception as e:
        await bot.send_message(chat_id, str(e))




# Funcion que se ejecuta al seleccionar la opcion "Rastrear Stock"
# @bot.message_handler(func=lambda action: True)
# async def process_stock_step(message):
#     url = message.text
#
#     regexp = re.compile(AMZ_REGEXP)
#     if regexp.match(url):  # Comprueba que la URL coincide con la ExpRegular de las URL de Amazon
#         await bot.send_message(message.chat.id, "La URL introducida es correcta")
#     else:
#         await bot.send_message(message.chat.id, "URL incorrecta 😢. Introduce un producto de Amazon válido")
#
#     if action == 'stock':
#         try:
#             # Obtenemos los datos de Amazon
#             await bot.send_message(message.chat.id, "Obteniendo stock...")
#             amz = AmzScraper()  # Realizamos scraping con la URL
#             stock = await amz.main(url, 'stock')  # Llamamos al metodo que obtiene el stock
#
#             if stock == 'En stock.':
#                 await bot.send_message(message.chat.id, f'Hey! Tu producto vuelve a estar disponible! 🤩'
#                                                         f'{url}')
#         except Exception as e:
#             # bot.reply_to(message, "Se ha producido un error durante el rastreo 😢")
#             await bot.reply_to(message, str(e))
#
#     if action == 'precio':
#         try:
#             # Obtenemos los datos de Amazon
#             await bot.send_message(message.chat.id, "Obteniendo precio...")
#             amz = AmzScraper()  # Realizamos scraping con la URL
#             precio = await amz.main(url, 'precio')  # Llamamos al metodo que obtiene el stock
#         except Exception as e:
#             await bot.reply_to(message, "Se ha producido un error durante el rastreo 😢")


# @bot.message_handler(func=lambda action: 'precio')
# async def process_prize_step(message):
#     action = None
#     url = message.text
#     try:
#         regexp = re.compile(AMZ_REGEXP)
#         if regexp.match(url):  # Comprueba que la URL coincide con la ExpRegular de las URL de Amazon
#             await bot.send_message(message.chat.id, "La URL introducida es correcta")
#         else:
#             await bot.send_message(message.chat.id, "URL incorrecta 😢. Introduce un producto de Amazon válido")
#
#         # Obtenemos los datos de Amazon
#         await bot.send_message(message.chat.id, "Obteniendo precio...")
#         amz = AmzScraper()  # Realizamos scraping con la URL
#         precio = await amz.main(url, 'precio')  # Llamamos al metodo que obtiene el stock
#
#         await bot.send_message(message.chat.id, f'El precio de este producto actualmente es {precio}')
#     except Exception as e:
#         await bot.reply_to(message, "Se ha producido un error durante el rastreo 😢")
#
# respuesta al comando /help
@bot.message_handler(commands=["help"])  # Se establece un decorador que responderá al comando /help
async def show_help(message):
    msg_help = f'🆘 <b>Ayuda</b> 🆘 \n\n' \
                f'<b>🔶 ¿Qué es Trackmazon?</b> \n' \
                f'   🔹 Trackmazon es un asistente que te ayuda a encontrar las mejores ofertas de productos de Amazon, ' \
                f'avisándote cuando un producto vuelva a tener stock o haya bajado su precio. \n\n' \
                f'<b>🔶 ¿Como funciona Trackmazon?</b> \n' \
                f'🔹 Para comenzar a usar Trackmazon escribe el comando /start.\n El bot te pedirá que introduzcas el enlace del' \
                f' producto que quieres rastrear.' \
                f' Cuando introduces una URL válida puedes escoger entre 2 opciones: \n     <b>1.</b> Rastrear el stock de un producto que no está disponible.' \
                f' Trackmazon te avisará cuando ese producto vuelva a tener stock.\n     <b>2.</b> Rastrear el precio de un producto. Trackmazon te avisará' \
                f' cuando el precio de un producto con stock esté por debajo del precio que has indicado.\n\n' \
                f'<b>🔶 ¿Como veo los productos que estoy rastreando?</b> \n' \
                f'🔹 Con el comando /list se mostrarán todos los productos que estás rastreando en ese momento.\n\n' \
                f'<b>🔶 ¿Qué hago si quiero dejar de rastrear un producto?</b> \n' \
                f'🔹 En el menú donde se muestran los productos que estas rastreando (/list) puedes elegir el' \
                f' producto que quieres eliminar\n'

    await bot.send_message(message.chat.id, msg_help, parse_mode="html")


# Responde a los mensajes de texto que no son comandos
@bot.message_handler(content_types=["text"])
# Gestiona mensajes de texto
async def text_messages(message):
    if message.text.startswith("/"):
        await bot.send_message(message.chat.id, "Comando no disponible")
    if message.text.startswith("http"):
        await bot.send_message(message.chat.id, "La URL introducida no es válida")
    else:
        await bot.send_message(message.chat.id, "No tengo respuesta para eso pero se me da bien rastrear productos 😉")


# --- MAIN ---
if __name__ == "__main__":
    freeze_support()
    # Enable saving next step handlers to file "./.handlers-saves/step.save".
    # Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
    # saving will happen after delay 2 seconds.
    # bot.enable_save_next_step_handlers(delay=2)

    # Load next_step_handlers from save file (default "./.handlers-saves/step.save")
    # WARNING It will work only if enable_save_next_step_handlers was called!
    # bot.load_next_step_handlers()

    # bot.infinity_polling()  # Permanece a la escucha de nuevos mensajes
    asyncio.run(bot.polling(non_stop=True, interval=3, timeout=30, request_timeout=300))
    print('Fin')
