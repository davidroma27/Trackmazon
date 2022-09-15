from config import *  # se importa el token e IDs
from amz import AmzScraper
import telebot  # Para importar la API de Telegram
from telebot.async_telebot import AsyncTeleBot  # Importamos el bot asincrono
from telebot import types
import asyncio
from telebot.types import InlineKeyboardMarkup  # Para crear menu de botones
from telebot.types import InlineKeyboardButton  # Para definir botones inline
from dbhelper import DBHelper
import re  # Para evaluar expresiones regulares
import nest_asyncio

nest_asyncio.apply()

# instacia del bot
bot = AsyncTeleBot(TLG_TOKEN)  # Le pasamos el token del bot a instanciar
db = DBHelper()  # Instancia de la base de datos
amz = AmzScraper()  # Instancia de la clase de scraping


# respuesta al comando /start
@bot.message_handler(commands=["start"])  # Se establece un decorador que responderá al comando /start
async def start(message):
    await bot.send_message(message.chat.id,
                           "👋 Bienvenido a Trackmazon! 👋 \n Para empezar introduce la URL de un producto")


# Responde a los mensajes que contienen una URL de Amazon
# Empleamos una regexp que indentifica URLs de Amazon
# https://regex101.com/r/UaxDyp/1
# ^([https?://www\.]*amazon\.(com|es|co\.uk|de|fr|it|nl)).*?(\/[dg]p\/[^/]+).*
@bot.message_handler(regexp=AMZ_REGEXP)
# Gestiona los mensajes con enlaces de amazon
async def handle_url(message):
    global url
    global urlMsg
    chat_id = message.chat.id
    urlMsg = message
    url = message.text
    await bot.reply_to(message, "La url introducida es correcta")

    markup = InlineKeyboardMarkup(row_width=1)  # Establecemos un boton por fila (3 por defecto)
    b_stock = InlineKeyboardButton("Rastrear stock 📈", callback_data="stock")
    b_precio = InlineKeyboardButton("Rastrear precio 💸", callback_data="precio")
    markup.add(b_stock, b_precio)  # Agregamos los botones al markup
    await bot.send_message(message.chat.id, "Elige la opción que quieres rastrear: ",
                           reply_markup=markup)


# Handler que responde a los botones del menu despues de introducir una URL válida
@bot.callback_query_handler(func=lambda call: call.data == 'stock' or call.data == 'precio')
async def respuesta_botones(call):  # Gestiona las acciones del menu de botones
    chat_id = call.from_user.id

    if call.data == 'stock':
        try:
            # Obtenemos los datos de Amazon
            await bot.send_message(chat_id, "Obteniendo stock...")
            stock = await amz.main(url, 'stock')  # Realiza el scraping para stock

            # Si el stock devuelve vacío muestra que no esta disponible
            if stock[1] == '':
                await bot.send_message(chat_id, f'Estado actual: No disponible.')
            else:  # Si no, muestra el estado del stock que muestra en la web
                await bot.send_message(chat_id, f'Estado actual: {stock[1]}')

            # Si no hay stock realiza el rastreo. Si hay stock no hace nada
            if stock[1] == '' or stock[1] == 'No disponible.':
                db.add_tracking(chat_id, url, stock[0], 'stock',
                                'No disponible.')  # Se almacena en la base de datos el nuevo rastreo
                await bot.send_message(chat_id, f'<b> Rastreando stock </b> ✅\n '
                                                f'🔷 {stock[0]}\n', parse_mode="html")
            else:  # Si el producto ya se encuentra en stock no se rastrea
                await bot.send_message(chat_id,
                                       f'Este producto ya se ecuentra en stock! Prueba a rastrear su precio 😉')

        except Exception as e:
            await bot.reply_to(call.message, "Se ha producido un error durante el rastreo 😢")
            # await bot.send_message(chat_id, str(e))

    if call.data == 'precio':
        global precio
        try:
            # Obtenemos los datos de Amazon
            await bot.send_message(chat_id, "Obteniendo precio...")
            stock = await amz.main(url, 'stock')  # Comprobamos que el producto esta disponible

            # Si no hay stock no realiza rastreo de precio
            if stock[1] == '' or stock[1] == 'No disponible.':
                await bot.send_message(chat_id, f'Estado actual: No disponible.')
                await bot.reply_to(urlMsg,
                                   f'El producto no tiene stock, imposible rastrear precio. Prueba a rastrear el stock! 😉')
            else:
                # Si hay stock rastrea el precio y lo almacena
                precio = await amz.main(url, 'precio')  # Realiza el scraping para precio
                trim = re.compile(r'[^\d.,]+')
                valor = trim.sub('', precio[1])

                db.add_tracking(chat_id, url, precio[0], 'precio',
                                valor)  # Se almacena en la base de datos el nuevo rastreo
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

    teclado = types.InlineKeyboardMarkup(row_width=3)
    for e in lista:
        msg += f'🔹 [{lista.index(e)}] - {e}\n'
        teclado.add(types.InlineKeyboardButton(f'[{lista.index(e)}]', callback_data=f'{lista.index(e)}'))

    if len(lista) > 0:
        msg += f'\nPuedes seleccionar debajo un producto para eliminar 👇'

    await bot.send_message(message.chat.id, msg, parse_mode="html", reply_markup=teclado)


# Responde al menú para elminiar un procuto del rastreo
@bot.callback_query_handler(func=lambda call: True)
async def eliminar_producto(req):
    chat_id = req.from_user.id
    titulo = lista[int(req.data)]
    producto = db.get_url(titulo).pop()[0]
    try:
        db.del_tracking(producto, chat_id)  # Se elimina el producto de la BD
        await bot.send_message(chat_id, f"El producto ha sido eliminado ✅")
    except Exception as e:
        await bot.send_message(chat_id, str(e))


# respuesta al comando /ayuda
@bot.message_handler(commands=["ayuda"])  # Se establece un decorador que responderá al comando /ayuda
async def show_help(message):
    msg_help = f'🆘 <b>Ayuda</b> 🆘 \n\n' \
               f'<b>🔶 ¿Qué es Trackmazon?</b> \n' \
               f'   🔹 Trackmazon es un asistente que te ayuda a encontrar las mejores ofertas de productos de Amazon, ' \
               f'avisándote cuando un producto vuelva a tener stock o haya bajado su precio. \n\n' \
               f'<b>🔶 ¿Como funciona Trackmazon?</b> \n' \
               f'🔹 Para comenzar a usar Trackmazon escribe el comando /start.\n El bot te pedirá que introduzcas el enlace del' \
               f' producto que quieres rastrear.' \
               f' Cuando introduces una URL válida puedes escoger entre 2 opciones: \n     1️⃣ Rastrear el stock de un producto que no está disponible.' \
               f' Trackmazon te avisará cuando ese producto vuelva a tener stock.\n     2️⃣ Rastrear el precio de un producto. Trackmazon te avisará' \
               f' cuando haya bajado el precio de ese producto.\n\n' \
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


# Rastrea los productos almacenados en la BD
async def product_checker():
    productos = db.get_all()  # Array de productos
    # Itera sobre todos los productos de la BD
    for p in productos:
        chat_id = p[0]
        link = p[1]
        opcion = p[3]
        estado = p[4]

        # await bot.send_message(chat_id, f"Rastreando producto {productos.index(p)}")
        newStock = await amz.main(link, 'stock')  # Realiza el scraping para stock

        try:
            # Si la opcion es stock rastrea el stock del producto
            if opcion == 'stock':

                if newStock[1] == 'En stock.':
                    await bot.send_message(chat_id, f'Hey! Tu producto vuelve a estar disponible! 🤑\n'
                                                    f'🔷 {link}')
                    db.update_estado(newStock[1], chat_id, link)  # Actualiza el estado en la BD
                else:
                    pass

            # Si la opcion del producto es precio rastrea el precio
            if opcion == 'precio':
                if newStock[1] == '' or newStock[1] == 'No disponible.':  # Si no tiene stock avisa al usuario
                    await bot.send_message(chat_id, f'Tu producto con rastreo de precio se ha quedado sin stock! 😢\n'
                                                    f'{link}')
                else:
                    newPrecio = await amz.main(link, 'precio')  # Si tiene stock obtiene el precio actual
                    # Formatea el valor del nuevo precio
                    trim = re.compile(r'[^\d.,]+')
                    valor = trim.sub('', newPrecio[1])
                    # Si el precio actual es menor que el almacenado en la BD se actualiza y notifica al usuario
                    if valor < estado:
                        await bot.send_message(chat_id, f'Hey! Tu producto ha bajado de precio! 🤑\n'
                                                        f'🔷 {link}')
                        db.update_estado(valor, chat_id, link)  # Actualiza el precio del producto
        except Exception as e:
            print(e)


# Funcion que gestiona la ejecucion de la funcion de rastreo pasadole un intervalo de tiempo
async def schedule_checker(interval, func):
    while True:
        await asyncio.gather(
            asyncio.sleep(interval),
            func()
        )


# Crea 2 tareas. Una para ejecutar el bot en general y otra para rastrear periodicamente los productos
async def main():
    task1 = asyncio.create_task(
        bot.polling(non_stop=True, interval=3, timeout=30, request_timeout=300))  # Ejecuta el bot polling
    task2 = asyncio.create_task(schedule_checker(300,
                                                 product_checker))  # Crea una tarea programada cada 5 minutos que ejecuta la funcion de rastreo
    await asyncio.gather(task1, task2)


# --- MAIN ---
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop = asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt as e:
        print("Caught KeyboardInterrupt. Canceling tasks...")
        loop.run_forever()
    finally:
        loop.close()