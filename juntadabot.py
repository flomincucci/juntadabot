#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hola, soy JuntadaBot

v0.1 Version inicial, sin soporte para multiples juntadas
"""

import logging
import redis
import telegram

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

r = redis.Redis(
        host='localhost',
        port=6379)

def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='¡Hola! Soy JuntadaBot!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Para crear una nueva juntada, manda /nueva_juntada <nombre_juntada>')


def nueva_juntada(bot, update):
    nombre_juntada = update.message.text[15:]
    grupo = update.message.chat_id
    if len(nombre_juntada) == 0:
        bot.sendMessage(update.message.chat_id,
                        text='Tenes que especificar el nombre de la juntada')
    else:
        r.set('%s_juntada' % grupo, nombre_juntada)
        bot.sendMessage(update.message.chat_id,text='Juntada "%s" creada.' % nombre_juntada)
        mostrar_teclado_rsvp(bot, update)


def vaciar_juntada(bot, update):
    grupo = update.message.chat_id
    r.delete('%(grupo)s_asistencias' % locals())
    bot.sendMessage(update.message.chat_id,text='Juntada vaciada.')


def eliminar_juntada(bot, update):
    grupo = update.message.chat_id
    r.delete('%s_asistencias' % grupo)
    r.delete('%s_juntada' % grupo)
    bot.sendMessage(update.message.chat_id,text='Juntada eliminada.')


def listar_asistentes(bot, update):
    grupo = update.message.chat_id
    asistencias = r.hgetall('%(grupo)s_asistencias' % locals())
    total_asistentes = 0
    texto = ""
    for persona in asistencias:
        texto += '* %s -> %s \n' % (persona, asistencias[persona])
        if (asistencias[persona] == "Va"):
            total_asistentes = total_asistentes + 1

    bot.sendMessage(update.message.chat_id,text=texto)
    bot.sendMessage(update.message.chat_id,text="Total asistentes: %i personas" % total_asistentes)


def rsvp(bot, update):
    mensaje = update.message.text
    if mensaje == "Voy":
        voy(bot, update)
    elif mensaje == "No voy":
        no_voy(bot, update)


def mostrar_teclado_rsvp(bot, update):
    grupo = update.message.chat_id
    custom_keyboard = [[ "Voy", "No voy" ]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                                resize_keyboard=True,
                                                one_time_keyboard=True)
    nombre_juntada = r.get('%s_juntada' % grupo)
    bot.sendMessage(chat_id=update.message.chat_id, text="¿Venís a %s?" % nombre_juntada,
                    reply_markup=reply_markup)


def voy(bot, update):
    grupo = update.message.chat_id
    usuario =  update.message.from_user
    r.hset('%(grupo)s_asistencias' % locals(), usuario.username, "Va")


def no_voy(bot, update):
    grupo = update.message.chat_id
    usuario =  update.message.from_user
    r.hset('%(grupo)s_asistencias' % locals(), usuario.username, "No va")


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = telegram.Updater(token=TOKEN)
    dp = updater.dispatcher

    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)

    dp.addTelegramCommandHandler("nueva_juntada", nueva_juntada)
    dp.addTelegramCommandHandler("vaciar_juntada", vaciar_juntada)
    dp.addTelegramCommandHandler("eliminar_juntada", eliminar_juntada)
    dp.addTelegramCommandHandler("listar_asistentes", listar_asistentes)

    dp.addTelegramCommandHandler("voy", voy)
    dp.addTelegramCommandHandler("no_voy", no_voy)

    dp.addTelegramMessageHandler(rsvp)
    dp.addErrorHandler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
