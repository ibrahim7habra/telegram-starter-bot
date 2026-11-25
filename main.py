import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعت لينك TikTok / YouTube / Facebook وانا احملهولك بدون علامة مائية 🎬")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" not in url:
        return
    msg = await update.message.reply_text("جارٍ التحميل... ⏳")
    try:
        ydl_opts = {
            'format': 'best[filesize<50M]/best',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_video(video=open(filename, 'rb'), caption="تم ✅ @ibrahim_habra_bot")
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"حصل خطأ، جرب لينك تاني ❌\n{e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
