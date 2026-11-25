import { exec } from "child_process";
import fs from "fs";
import path from "path";

export function registerDownloader(bot) {
  bot.on("text", async (ctx) => {
    const text = ctx.message?.text?.trim();
    if (!text || !text.startsWith("http")) return;
    if (text.startsWith("/")) return;

    const msg = await ctx.reply("⏳ جاري التحميل... استنى ثواني");
    const outDir = "/tmp";
    const outFile = path.join(outDir, `dl_${Date.now()}.mp4`);

    const cmd = `yt-dlp -f "mp4[height<=720]/best[ext=mp4]/best" -o "${outFile}" "${text}"`;

    exec(cmd, async (err) => {
      try {
        if (err || !fs.existsSync(outFile)) {
          await ctx.telegram.editMessageText(ctx.chat.id, msg.message_id, undefined, "❌ مقدرتش أحمل الرابط ده، جرب رابط تاني.");
          return;
        }
        await ctx.replyWithVideo({ source: outFile }, { caption: "✅ تم التحميل" });
        await ctx.telegram.deleteMessage(ctx.chat.id, msg.message_id).catch(() => {});
        fs.unlinkSync(outFile);
      } catch (e) {
        await ctx.reply("❌ حصل خطأ أثناء الإرسال");
      }
    });
  });
}
