import sqlite3


def create_database():
    conn = sqlite3.connect("productos.db")
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS productos
                     (Codigo INTEGER PRIMARY KEY,
                     Producto TEXT,
                     Precio REAL,
                     Cantidad INTEGER)"""
    )
    conn.commit()
    conn.close()


create_database()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)

# Cambia 'TOKEN' por el token que recibiste al crear el bot en Telegram
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"


def start(update: Update, _: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Insertar productos", callback_data="insertar")],
        [InlineKeyboardButton("Actualizar productos", callback_data="actualizar")],
        [InlineKeyboardButton("Borrar productos", callback_data="borrar")],
        [InlineKeyboardButton("Consultar productos", callback_data="consultar")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selecciona una opción:", reply_markup=reply_markup)


def button_callback(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "insertar":
        query.edit_message_text(
            "Por favor, envía la información del producto en el siguiente formato:\n\n"
            "/insertar Codigo Producto Precio Cantidad"
        )
    elif query.data == "actualizar":
        query.edit_message_text(
            "Por favor, envía la información del producto que deseas actualizar en el siguiente formato:\n\n"
            "/actualizar Codigo Producto Precio Cantidad"
        )
    elif query.data == "borrar":
        query.edit_message_text(
            "Por favor, envía el código del producto que deseas eliminar en el siguiente formato:\n\n"
            "/borrar Codigo"
        )
    elif query.data == "consultar":
        query.edit_message_text("Consultando productos...")
        consultar_productos(update, _)


def insertar_producto(update: Update, _: CallbackContext):
    info_producto = update.message.text.split()[1:]
    if len(info_producto) != 4:
        update.message.reply_text(
            "Por favor, verifica el formato de la información del producto y vuelve a intentarlo."
        )
        return

    codigo, producto, precio, cantidad = info_producto
    conn = sqlite3.connect("productos.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (Codigo, Producto, Precio, Cantidad) VALUES (?, ?, ?, ?)",
        (codigo, producto, precio, cantidad),
    )
    conn.commit()
    conn.close()
    update.message.reply_text("Producto insertado correctamente.")


def actualizar_producto(update: Update, _: CallbackContext):
    info_producto = update.message.text.split()[1:]
    if len(info_producto) != 4:
        update.message.reply_text(
            "Por favor, verifica el formato de la información del producto y vuelve a intentarlo."
        )
        return
    codigo, producto, precio, cantidad = info_producto
    conn = sqlite3.connect("productos.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET Producto = ?, Precio = ?, Cantidad = ? WHERE Codigo = ?",
        (producto, precio, cantidad, codigo),
    )
    conn.commit()
    conn.close()

    if cursor.rowcount > 0:
        update.message.reply_text("Producto actualizado correctamente.")
    else:
        update.message.reply_text(
            "No se encontró el producto con el código proporcionado."
        )


def borrar_producto(update: Update, _: CallbackContext):
    codigo = update.message.text.split()[1]
    if not codigo:
        update.message.reply_text(
            "Por favor, verifica el formato del código del producto y vuelve a intentarlo."
        )
        return

    conn = sqlite3.connect("productos.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE Codigo = ?", (codigo,))
    conn.commit()
    conn.close()

    if cursor.rowcount > 0:
        update.message.reply_text("Producto eliminado correctamente.")
    else:
        update.message.reply_text(
            "No se encontró el producto con el código proporcionado."
        )


def consultar_productos(update: Update, _: CallbackContext):
    conn = sqlite3.connect("productos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        response = "Productos en la base de datos:\n\n"
        for row in rows:
            response += f"Codigo: {row[0]}, Producto: {row[1]}, Precio: {row[2]}, Cantidad: {row[3]}\n"
        update.callback_query.edit_message_text(response)
    else:
        update.callback_query.edit_message_text("No hay productos en la base de datos.")


def main():
    updater = Updater("6145668172:AAE_njqesomtFq7gGflGAFRE6YmV282K3Tk")

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    dispatcher.add_handler(CommandHandler("insertar", insertar_producto))
    dispatcher.add_handler(CommandHandler("actualizar", actualizar_producto))
    dispatcher.add_handler(CommandHandler("borrar", borrar_producto))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
