using DotNetEnv;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using Telegram.Bot;
using Telegram.Bot.Args;
using Telegram.Bot.Types;
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
            using (var stream = System.IO.File.OpenRead(".env.debug"))
#else
            using (var stream = System.IO.File.OpenRead(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "VorishkaBot", ".env")))
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

            // New user
            if (e.Message.Text == "/start")
            {
                // Remove user data on restart
                if (UserMapping.ContainsKey(userId))
                {
                    Db.DeleteUser(userId);
                    UserMapping.Remove(userId);
                }

                await Bot.SendTextMessageAsync(userId, "Пришли мне свой первый стикер");
            }

            if (!UserMapping.ContainsKey(e.Message.From.Id))
            {
                UserMapping.Add(userId, null);
                Db.NewMsg(Db.MsgTypes.INFO, $"New user: {userId}", userId);
            }

            // Process received message
            switch (e.Message.Type)
            {
                case MessageType.Sticker:
                    {
                        if (e.Message.Sticker.IsAnimated)
                        {
                            OnAnimatedSticker(e.Message, userId);
                        }
                        else
                        {
                            OnSticker(e.Message, userId);
                        }
                        break;
                    }
                case MessageType.Photo:
                    {
                        OnPhoto(e.Message, userId);
                        break;
                    }
            }
        }

        private static async void OnSticker(Message message, int userId)
        {
            // Download WEBP sticker
            var webpFilename = Converter.GetRandomName() + ".webp";
            await Converter.DownloadTgFile(webpFilename, message.Sticker.FileId, userId);

            // Convert sticker to PNG
            var pngFilename = Converter.ToPng(webpFilename);
            pngFilename = Converter.QuantifyPng(pngFilename);

            AddSticker(userId, pngFilename, message.Sticker.Emoji, message.MessageId);
        }

        private static async void OnAnimatedSticker(Message message, int userId)
        {
            await Bot.SendTextMessageAsync(userId, "Я пока не умею сохранять анимированные стикеры :c", ParseMode.Default, false, false, message.MessageId);
        }

        private static async void OnPhoto(Message message, int userId)
        {
            string fileId = message.Photo.ToList().OrderByDescending(f => Math.Max(f.Width, f.Height)).First().FileId;
            string saveFilename = Converter.GetRandomName() + ".jpg";
            await Converter.DownloadTgFile(saveFilename, fileId, userId);
            saveFilename = Converter.ToPng(saveFilename);
            saveFilename = Converter.ResizePng(saveFilename);
            saveFilename = Converter.QuantifyPng(saveFilename);
            // TODO: ask for emoji
            AddSticker(userId, saveFilename, "\ud83d\ude02", message.MessageId);
        }
        private static async void AddSticker(int userId, string pngFilename, string emoji, int messageId)
        {
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
                        await Bot.SendTextMessageAsync(userId, "Я не смог сохранить стикер, попробуй еще раз", ParseMode.Default, false, false, messageId);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, userId, ex.StackTrace);
                await Bot.SendTextMessageAsync(userId, "Я не смог сохранить стикер, попробуй еще раз", ParseMode.Default, false, false, messageId);                
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
