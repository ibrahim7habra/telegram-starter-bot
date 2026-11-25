import os
import re
import glob
import shutil
import asyncio
import tempfile
import requests
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
TOKEN = os.getenv("BOT_TOKEN", "9060575501:AAHBFRqcuHJAB2VLs4eJusprhl5L_FYpXc8")
MAX_SIZE = 50 * 1024 * 1024
URL_RE = re.compile(r"https?://\S+")
HEADERS = {
"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
"Referer": "https://www.tiktok.com/",
}
def opts(folder): return {
"outtmpl": os.path.join(folder, "%(id)s.%(ext)s"),
"format": "best[ext=mp4][filesize<50M]/best[ext=mp4]/best",
"noplaylist": True,
"quiet": True,
"no_warnings": True,
"max_filesize": MAX_SIZE,
"socket_timeout": 20,
"http_headers": {"User-Agent": HEADERS["User-Agent"]},
}
def download_ytdlp(url, folder): YoutubeDL(opts(folder)).download([url]); return glob.glob(os.path.join(folder, "*"))[0]
def download_tikwm(url, folder): res = requests.get("https://www.tikwm.com/api/", params={"url": url}, headers=HEADERS, timeout=20).json(); assert res.get("code") == 0, "tikwm failed"; v = requests.get(res["data"]["play"], headers=HEADERS, timeout=60); assert len(v.content) > 10000, "empty video"; path = os.path.join(folder, "tiktok.mp4"); open(path, "wb").write(v.content); return path
async def run(url, folder): r = (await asyncio.gather(asyncio.to_thread(download_ytdlp, url, folder), return_exceptions=True))[0]; return (await asyncio.gather(asyncio.to_thread(download_tikwm, url, folder), return_exceptions=True))[0] if isinstance(r, Exception) and "tiktok.com" in url else r
async def send_video(update, status, path): await update.message.reply_video(video=open(path, "rb"), caption="خلص ✅", supports_streaming=True, read_timeout=120, write_timeout=120); await status.delete()
async def deliver(update, status, r): await (status.edit_text("معرفتش أنزل الفيديو ❌ جرب لينك تاني.\n(" + str(r)[:150] + ")") if isinstance(r, Exception) else status.edit_text("الفيديو أكبر من 50 ميجا، تليجرام مش بيسمح برفعه ❌") if os.path.getsize(r) > MAX_SIZE else send_video(update, status, r))
async def process(update, url): status = await update.message.reply_text("بنزل... ⏳"); folder = tempfile.mkdtemp(); r = await run(url, folder); d = (await asyncio.gather(deliver(update, status, r), return_exceptions=True))[0]; await (asyncio.gather(status.edit_text("فشل إرسال الفيديو ❌"), return_exceptions=True) if isinstance(d, Exception) else asyncio.sleep(0)); shutil.rmtree(folder, ignore_errors=True)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("ابعتلي لينك فيديو من تيك توك / انستجرام / فيسبوك / تويتر / يوتيوب / ريديت وأنا أنزله ✅")
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE): m = URL_RE.search(update.message.text or ""); await (process(update, m.group(0)) if m else update.message.reply_text("ابعت لينك صحيح 🔗"))
def main(): app = ApplicationBuilder().token(TOKEN).build(); app.add_handler(CommandHandler("start", start)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)); app.run_polling()
if __name__ == "__main__": main()
