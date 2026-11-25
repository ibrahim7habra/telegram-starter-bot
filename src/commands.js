import { exec } from "child_process";
import fs from "fs";
import util from "util";
const execAsync = util.promisify(exec);

const isLink = (text) => /https?:\/\/(www\.)?(tiktok\.com|youtube\.com|youtu\.be|facebook\.com|fb\.watch|instagram\.com|instagr\.am)/i.test(text);

export default function registerCommands(bot) {
  bot.start((ctx) => ctx.reply("أهلا بيك 👋\nابعتلي لينك صورة أو فيديو من تيك توك / يوتيوب / فيسبوك / انستجرام"));
  bot.help((ctx) => ctx.reply("ابعت أي لينك صورة أو فيديو"));
  bot.on("text", async (ctx) => {
    const text = ctx.message.text;
    if (text.startsWith("/")) return;
    if (!isLink(text)) return ctx.reply("ابعت لينك صحيح");
    const msg = await ctx.reply("⏳ جاري التحميل...");
    const out = `/tmp/${Date.now()}`;
    try {
      await execAsync(`yt-dlp --no-playlist --max-filesize 45M -o "${out}.%(ext)s" "${text}"`);
      const files = fs.readdirSync("/tmp").filter(f => f.startsWith(out.split("/").pop()));
      if (files.length === 0) throw new Error("فشل");
      for (const f of files) {
        const full = `/tmp/${f}`;
        if (/\.(jpg|jpeg|png|webp)$/i.test(f)) {
          await ctx.replyWithPhoto({ source: full });
        } else {
          await ctx.replyWithVideo({ source: full });
        }
        fs.unlinkSync(full);
      }
      await ctx.deleteMessage(msg.message_id);
    } catch (e) {
      await ctx.reply("❌ مقدرتش احمل ده، جرب لينك تاني أو اتأكد انه مش خاص");
    }
  });
}
