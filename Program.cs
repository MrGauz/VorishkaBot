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

                await Bot.SendTextMessageAsync(
                    chatId: userId,
                    text: "Привет! Я сохраняю твои любимые стикеры в один пак, чтобы тебе не приходилось тратить полдня чтобы найти любимый кек по десяткам сохраненных тобой стикерпаков. Смотри на меня, как на улучшенную версию <i>“Favourites”</i>: она позволяет хранить в себе до 5 стикеров, я же сохраню вплоть до 120, больше Telegram в один пак сохранять не позволяет.\n\n" +
                            "<b>Что я могу?</b>\n" +
                            "\u2705 Сохранять статичные стикеры\n" +
                            "\u2705 Делать стикеры из картинок\n\n" +
                            "<b>Чего я не могу?</b>\n" +
                            "\u274c Сохранять анимированные стикеры\n" +
                            "\u274c Удалять стикеры из стикерпака или менять их порядок\n\n" +
                            "<b>Что нужно учесть?</b>\n" +
                            "\u23f3 Добавление стикера не происходит мгновенно. Telegram говорит, что добавление стикера в стикерпак занимает до часа времени. На самом деле, это дело одной - двух минут, но если только что добавленный стикер не появился в стикерпаке сразу же — подожди. Это не баг, это фича.\n" +
                            "\u2b07\ufe0f Не забудь <i>сохранить</i> стикерпак.\n" +
                            "\ud83d\udee0 Если нужно что-то поправить в паке, воспользуйся официальным <a href=\"https://t.me/Stickers\">Stickers-ботом</a> Telegram’а. В нём можно менять порядок стикеров, менять эмодзи и удалять стикеры из стикерпака.\n\n" +
                            "\ud83d\udcec Пришли мне свой первый стикер или картинку, из которой ты хотел бы стикер.",
                    parseMode: ParseMode.Html
                    );
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
            var webpFilename = Converter.GetRandomName() + ".webp";
            await Converter.DownloadTgFile(webpFilename, message.Sticker.FileId, userId);
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
                            text: $"\u2705 Стикер успешно сохранен в [вот сюда](t.me/addstickers/{UserMapping[userId]})\\. Не забудь сохранить этот стикерпак\\.",
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
                        await Bot.SendTextMessageAsync(userId, "\u274c Task failed successfully. Попробуй еще раз.", ParseMode.Default, false, false, messageId);
                        return;
                    }

                    await Bot.SendTextMessageAsync(userId, "\u2705 Стикер сохранен", ParseMode.Default, false, false, messageId);
                }                
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, userId, ex.StackTrace);
                await Bot.SendTextMessageAsync(userId, "\u274c Task failed successfully. Попробуй еще раз.", ParseMode.Default, false, false, messageId);                
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
