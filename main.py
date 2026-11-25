import os
import re
import glob
import shutil
import subprocess
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
"format": "best[vcodec!=none][acodec!=none][ext=mp4]/best[vcodec!=none][ext=mp4]/best[vcodec!=none]/best",
"format_sort": ["vcodec:h264", "res", "ext:mp4:m4a"],
"noplaylist": True,
"cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
"quiet": True,
"no_warnings": True,
"max_filesize": MAX_SIZE,
"socket_timeout": 20,
"http_headers": {"User-Agent": HEADERS["User-Agent"]},
}
def download_ytdlp(url, folder): YoutubeDL(opts(folder)).download([url]); return glob.glob(os.path.join(folder, "*"))[0]
def ffexe(): return __import__("imageio_ffmpeg").get_ffmpeg_exe()
def has_video(path): return "Video:" in subprocess.run([ffexe(), "-i", path], capture_output=True, text=True, timeout=60).stderr
def tikwm_video(data, folder): v = requests.get(data.get("hdplay") or data["play"], headers=HEADERS, timeout=60); assert len(v.content) > 10000, "empty video"; path = os.path.join(folder, "tiktok.mp4"); open(path, "wb").write(v.content); return path
def tikwm_slide(data, folder): blobs = b"".join([requests.get(u, headers=HEADERS, timeout=30).content for u in data["images"]]); aud = os.path.join(folder, "audio.mp3"); open(aud, "wb").write(requests.get(data.get("music") or data["play"], headers=HEADERS, timeout=60).content); out = os.path.join(folder, "slideshow.mp4"); res = subprocess.run([ffexe(), "-y", "-f", "image2pipe", "-framerate", "1/3", "-i", "-", "-i", aud, "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,format=yuv420p", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-shortest", "-movflags", "+faststart", out], input=blobs, capture_output=True, timeout=300); assert res.returncode == 0, "slideshow failed"; return out
def download_tikwm(url, folder): full = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True).url; res = requests.get("https://www.tikwm.com/api/", params={"url": full, "hd": 1}, headers=HEADERS, timeout=30).json(); assert res.get("code") == 0, res.get("msg"); data = res["data"]; return tikwm_slide(data, folder) if data.get("images") else tikwm_video(data, folder)
def fix_video(path): out = os.path.splitext(path)[0] + "_h264.mp4"; res = subprocess.run([__import__("imageio_ffmpeg").get_ffmpeg_exe(), "-y", "-i", path, "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", out], capture_output=True, timeout=300); return out if res.returncode == 0 and os.path.exists(out) else path
async def run(url, folder): r = (await asyncio.gather(asyncio.to_thread(download_ytdlp, url, folder), return_exceptions=True))[0]; hv = (await asyncio.gather(asyncio.to_thread(has_video, r), return_exceptions=True))[0]; bad = isinstance(r, Exception) or hv is False; return (await asyncio.gather(asyncio.to_thread(download_tikwm, url, folder), return_exceptions=True))[0] if bad and "tiktok.com" in url else r
async def send_video(update, status, path): await update.message.reply_video(video=open(path, "rb"), caption="خلص ✅", supports_streaming=True, read_timeout=120, write_timeout=120); await status.delete()
async def deliver(update, status, r): await (status.edit_text("معرفتش أنزل الفيديو ❌ جرب لينك تاني.\n(" + str(r)[:150] + ")") if isinstance(r, Exception) else status.edit_text("الفيديو أكبر من 50 ميجا، تليجرام مش بيسمح برفعه ❌") if os.path.getsize(r) > MAX_SIZE else send_video(update, status, r))
async def process(update, url): status = await update.message.reply_text("بنزل... ⏳"); folder = tempfile.mkdtemp(); r = await run(url, folder); f = (await asyncio.gather(asyncio.to_thread(fix_video, r), return_exceptions=True))[0] if not isinstance(r, Exception) else r; r = r if isinstance(f, Exception) else f; d =(await asyncio.gather(deliver(update, status, r), return_exceptions=True))[0]; await (asyncio.gather(status.edit_text("فشل إرسال الفيديو ❌"), return_exceptions=True) if isinstance(d, Exception) else asyncio.sleep(0)); shutil.rmtree(folder, ignore_errors=True)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("ابعتلي لينك فيديو من تيك توك / انستجرام / فيسبوك / تويتر / يوتيوب / ريديت وأنا أنزله ✅")
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE): m = URL_RE.search(update.message.text or ""); await (process(update, m.group(0)) if m else update.message.reply_text("ابعت لينك صحيح 🔗"))
def main(): app = ApplicationBuilder().token(TOKEN).build(); app.add_handler(CommandHandler("start", start)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)); app.run_polling()
if __name__ == "__main__": main()
