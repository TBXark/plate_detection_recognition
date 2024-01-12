import asyncio
from threading import Thread

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import config
from recognition import Recognition, ImageWrapper
from utils import render_caption


class RecognitionBot:
    def __init__(self, _rec, _opt, _alert_opt):
        self.rec = _rec
        self.opt = _opt
        self.alert_opt = _alert_opt
        self.app = Application.builder().token(_opt.telegram_token).build()

    def start_bot(self):
        print('start telegram bot')
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("current", self.current_command))
        self.app.run_polling(read_timeout=120, timeout=120)

    def notify_callback(self, plates, jpg):
        loop = asyncio.new_event_loop()
        for cid in self.opt.telegram_chat_id:
            loop.run_until_complete(self.send_plate_alert_to_telegram(plates, jpg, cid))

    async def send_plate_alert_to_telegram(self, plates, jpg, chat_id):
        if plates is not None and len(plates) > 0:
            caption, disable_notification = render_caption(plates, self.alert_opt)
            await self.app.bot.send_photo(chat_id=chat_id, photo=jpg, caption=caption,
                                          disable_notification=disable_notification)
        else:
            await self.app.bot.send_photo(chat_id=chat_id, photo=jpg, disable_notification=True)

    def is_valid_chat_id(self, chat_id):
        return chat_id in self.opt.telegram_chat_id

    async def current_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self.is_valid_chat_id(update.message.chat_id):
            return
        raw = self.fetch_image()
        plates = self.rec.get_plates(raw.toFrame())
        await self.send_plate_alert_to_telegram(plates, raw.toJPEG(), update.message.chat_id)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self.is_valid_chat_id(update.message.chat_id):
            return
        await update.message.reply_text(f'Your ID is {update.message.chat_id}')

    def fetch_image(self):
        jpg = requests.get(self.opt.camera_api).content
        if jpg is None:
            return None
        return ImageWrapper(frame=None, jpg=jpg)


if __name__ == '__main__':

    opt = config.auto_load_config()
    rec = Recognition(opt.rec)
    bot = RecognitionBot(rec, opt.bot, opt.alert)

    if opt.rec.auto_recognition:
        Thread(target=rec.start, name="rec", args=(bot.fetch_image, bot.notify_callback), daemon=True).start()

    bot.start_bot()
