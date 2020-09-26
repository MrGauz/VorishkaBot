using DotNetEnv;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using Telegram.Bot;
using Telegram.Bot.Args;
using Telegram.Bot.Types.Enums;
using Telegram.Bot.Types.InputFiles;

namespace VorishkaBot
{
    class Program
    {
        public static ITelegramBotClient Bot;
        private static String BotName;
        private static Dictionary<int, string> UserMapping;

        public static void Main(string[] args)
        {
            // Init
#if DEBUG
            using (var stream = File.OpenRead(".env.debug"))
#else
            using (var stream = File.OpenRead(".env"))
#endif
            {
                Env.Load(stream);
                Bot = new TelegramBotClient(Env.GetString("TOKEN"));
                BotName = Env.GetString("BOT_NAME");
            }
            
            Db.Initialize(BotName);
            UserMapping = Db.GetUsers();

            // Fire up
            Bot.OnMessage += Bot_OnMessage;
            Bot.StartReceiving();
            WaitForKey();
            Bot.StopReceiving();
        }

        private static async void Bot_OnMessage(object sender, MessageEventArgs e)
        {
            int user_id = e.Message.From.Id;

            // New user
            if (!UserMapping.ContainsKey(e.Message.From.Id))
            {
                if (e.Message.Text == "/start")
                {
                    await Bot.SendTextMessageAsync(user_id, "Пришли мне свой первый стикер");
                }
                UserMapping.Add(user_id, null);
                Console.WriteLine($"[INFO] {DateTime.Now:yyyy-MM-dd HH:mm:ss} - New user: {user_id}");
                Db.NewMsg(Db.MsgTypes.INFO, $"New user: {user_id}", user_id);
            }

            // Receive sticker
            if (e.Message.Type == MessageType.Sticker)
            {
                if (e.Message.Sticker.IsAnimated)
                {
                    await Bot.SendTextMessageAsync(user_id, "Я пока не умею сохранять анимированные стикеры :c", ParseMode.Default, false, false, e.Message.MessageId);
                    return;
                }

                string emoji = e.Message.Sticker.Emoji;

                // Download WEBP sticker
                var savePath = Converter.GetRandomName() + ".webp";
                Converter.DowndloadSticker(savePath, e.Message.Sticker.FileId, user_id);
                
                // Convert sticker to PNG
                var convertPath = Converter.WebpToPng(savePath);
                Console.WriteLine($"[INFO] {DateTime.Now:yyyy-MM-dd HH:mm:ss} - Downloaded and converted sticker: {e.Message.Sticker.FileId} (for {user_id})");

                try
                {
                    InputOnlineFile newSticker = new InputOnlineFile(new FileStream(Path.Combine(Path.GetTempPath(), convertPath), FileMode.Open));

                    // Create new sticker set
                    if (UserMapping[user_id] == null)
                    {
                        UserMapping[user_id] = "sohranenki_" + DateTime.Now.Ticks.ToString().Substring(8, 7) + "_by_" + BotName;
                        Db.NewUser(user_id, UserMapping[user_id]);
                        try
                        {
                            await Bot.CreateNewStickerSetAsync(user_id, UserMapping[user_id], "Сохраненки", newSticker, emoji);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                            Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, user_id, ex.StackTrace);
                            return;
                        }
                        Console.WriteLine($"[INFO] {DateTime.Now:yyyy-MM-dd HH:mm:ss} - New set: {UserMapping[user_id]} ({user_id})");
                        await Bot.SendTextMessageAsync(
                                chatId: user_id,
                                text: $"Твои стикеры будут появляться здесь \ud83d\udc47\ud83c\udffb \n[\ud83d\uddbc Твои сохраненки](t.me/addstickers/{UserMapping[user_id]})",
                                parseMode: ParseMode.MarkdownV2
                                );
                    }

                    // Add to existing sticker set
                    else
                    {
                        try
                        {
                            await Bot.AddStickerToSetAsync(user_id, UserMapping[user_id], newSticker, emoji);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                            Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, user_id, ex.StackTrace);
                            await Bot.SendTextMessageAsync(user_id, "Я не смог сохранить стикер, попробуй еще раз", ParseMode.Default, false, false, e.Message.MessageId);
                        }
                    }
                } 
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                    await Bot.SendTextMessageAsync(user_id, "Я не смог сохранить стикер, попробуй еще раз", ParseMode.Default, false, false, e.Message.MessageId);
                    return;
                }

                // Clean up
                //File.Delete(Path.Combine(Path.GetTempPath(), convertPath));
            }
        }

        private static void WaitForKey()
        {
            Console.WriteLine("Press ESC to stop");
            do
            {
                while (!Console.KeyAvailable)
                {
                    Thread.Sleep(100);
                }
            } while (Console.ReadKey(true).Key != ConsoleKey.Escape);
        }
    }
}
