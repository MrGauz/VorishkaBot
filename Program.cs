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
            using (var stream = File.OpenRead(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".env")))
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
            int userId = e.Message.From.Id;

            // Remove user data on restart
            if (e.Message.Text == "/start")
            {
                if (UserMapping.ContainsKey(userId))
                {
                    Db.DeleteUser(userId);
                    UserMapping.Remove(userId);
                }
            }

            // New user
            if (!UserMapping.ContainsKey(e.Message.From.Id))
            {
                if (e.Message.Text == "/start")
                {
                    await Bot.SendTextMessageAsync(userId, "Пришли мне свой первый стикер");
                }
                UserMapping.Add(userId, null);
                Db.NewMsg(Db.MsgTypes.INFO, $"New user: {userId}", userId);
            }

            // Receive sticker
            if (e.Message.Type == MessageType.Sticker)
            {
                if (e.Message.Sticker.IsAnimated)
                {
                    await Bot.SendTextMessageAsync(userId, "Я пока не умею сохранять анимированные стикеры :c", ParseMode.Default, false, false, e.Message.MessageId);
                    return;
                }

                string emoji = e.Message.Sticker.Emoji;

                // Download WEBP sticker
                var webpFilename = Converter.GetRandomName() + ".webp";
                Converter.DowndloadSticker(webpFilename, e.Message.Sticker.FileId, userId);

                // Convert sticker to PNG
                var pngFilename = Converter.WebpToPng(webpFilename);
                pngFilename = Converter.QuantifyPng(pngFilename);

                try
                {
                    InputOnlineFile newSticker = new InputOnlineFile(new FileStream(Path.Combine(Path.GetTempPath(), pngFilename), FileMode.Open));

                    // Create new sticker set
                    if (UserMapping[userId] == null)
                    {
                        UserMapping[userId] = "sohranenki_" + DateTime.Now.Ticks.ToString().Substring(8, 7) + "_by_" + BotName;
                        Db.NewUser(userId, UserMapping[userId]);
                        try
                        {
                            await Bot.CreateNewStickerSetAsync(userId, UserMapping[userId], "Сохраненки", newSticker, emoji);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                            Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, userId, ex.StackTrace);
                            return;
                        }
                        await Bot.SendTextMessageAsync(
                                chatId: userId,
                                text: $"Твои стикеры будут появляться здесь \ud83d\udc47\ud83c\udffb \n[\ud83d\uddbc Твои сохраненки](t.me/addstickers/{UserMapping[userId]})",
                                parseMode: ParseMode.MarkdownV2
                                );
                    }

                    // Add to existing sticker set
                    else
                    {
                        try
                        {
                            await Bot.AddStickerToSetAsync(userId, UserMapping[userId], newSticker, emoji);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                            Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, userId, ex.StackTrace);
                            await Bot.SendTextMessageAsync(userId, "Я не смог сохранить стикер, попробуй еще раз", ParseMode.Default, false, false, e.Message.MessageId);
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                    Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, userId, ex.StackTrace);
                    await Bot.SendTextMessageAsync(userId, "Я не смог сохранить стикер, попробуй еще раз", ParseMode.Default, false, false, e.Message.MessageId);
                    return;
                }
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
