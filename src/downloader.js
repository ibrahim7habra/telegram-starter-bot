// downloader.js - تحميل فيديو من لينك على طول بدون علامة مائية
export function registerDownloader(bot) {
  bot.on("message:text", async (ctx) => {
    const text = ctx.message?.text?.trim() || "";
    if (!text.startsWith("http")) return;
    if (text.startsWith("/")) return;

    const isSupported =
      text.includes("youtube.com") ||
      text.includes("youtu.be") ||
      text.includes("tiktok.com") ||
      text.includes("instagram.com") ||
      text.includes("facebook.com") ||
      text.includes("fb.watch");

    if (!isSupported) return;

    await ctx.reply("⏳ جاري تحميل الفيديو...");

    try {
      const res = await fetch("https://api.cobalt.tools", {
        method: "POST",
        headers: {
          Accept
