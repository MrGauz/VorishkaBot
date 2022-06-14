using Serilog;
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
    public class Bot
    {
        public static ITelegramBotClient BotClient;
        private static string BotName;
        private static Dictionary<int, string> UserMapping;

        public static void StartReceiving(string botName, string token)
        {
            BotName = botName;
            UserMapping = Db.GetUsers();
            BotClient = new TelegramBotClient(token);
            BotClient.OnMessage += Bot_OnMessage;
            BotClient.StartReceiving();
        }

        private static async void Bot_OnMessage(object sender, MessageEventArgs e)
        {
            int userId = e.Message.From.Id;
            Log.Information($"Received a message from {userId}");
            
            // New user
            if (e.Message.Text == "/start")
            {
                _ = BotClient.SendChatActionAsync(userId, ChatAction.Typing, CancellationToken.None);

                // Remove user data on restart
                if (UserMapping.ContainsKey(userId))
                {
                    Db.DeleteUser(userId);
                    UserMapping.Remove(userId);
                }

                var sentMessage = await BotClient.SendTextMessageAsync(
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
                _ = BotClient.PinChatMessageAsync(userId, sentMessage.MessageId, true, CancellationToken.None);
                Log.Information($"Sent welcome message to {userId}");
            }
            else if (e.Message.Text == "/ping")
            {
                _ = BotClient.SendChatActionAsync(userId, ChatAction.Typing, CancellationToken.None);
                _ = BotClient.SendTextMessageAsync(
                       chatId: userId,
                       text: "Bot is running");
                Log.Information($"Pinged by {userId}");
            }

            if (!UserMapping.ContainsKey(e.Message.From.Id))
            {
                UserMapping.Add(userId, null);
                Log.Information($"New user: {userId}", userId);
            }

            // Process received message
            switch (e.Message.Type)
            {
                case MessageType.Sticker:
                    {
                        _ = BotClient.SendChatActionAsync(userId, ChatAction.Typing, CancellationToken.None);

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
                        _ = BotClient.SendChatActionAsync(userId, ChatAction.Typing, CancellationToken.None);
                        OnPhoto(e.Message, userId);
                        break;
                    }
            }
        }

        private static async void OnSticker(Message message, int userId)
        {
            Log.Information($"Received a sticker from {userId}");
            var filename = Path.Combine(Path.GetTempPath(), $"VorishkaBot_{Converter.GetRandomName()}.webp");

            await Converter.DownloadTgFile(filename, message.Sticker.FileId, userId);
            filename = Converter.ToPng(filename);
            filename = Converter.QuantifyPng(filename);

            AddSticker(userId, filename, message.Sticker.Emoji, message.MessageId);
        }

        private static void OnAnimatedSticker(Message message, int userId)
        {
            Log.Information($"Received an animated sticker from {userId}");
            _ = BotClient.SendTextMessageAsync(userId, "Я пока не умею сохранять анимированные стикеры :c", ParseMode.Default, false, false, message.MessageId);
        }

        private static async void OnPhoto(Message message, int userId)
        {
            Log.Information($"Received a photo from {userId}");
            var fileId = message.Photo.ToList().OrderByDescending(f => Math.Max(f.Width, f.Height)).First().FileId;
            var filename = Path.Combine(Path.GetTempPath(), $"VorishkaBot_{Converter.GetRandomName()}.jpg");

            await Converter.DownloadTgFile(filename, fileId, userId);
            filename = Converter.ToPng(filename);
            filename = Converter.ResizePng(filename);
            filename = Converter.QuantifyPng(filename);

            // TODO: ask for emoji
            AddSticker(userId, filename, "\ud83d\ude02", message.MessageId);
        }

        private static void AddSticker(int userId, string pngFilename, string emoji, int messageId)
        {
            try
            {
                var newSticker = new InputOnlineFile(new FileStream(Path.Combine(Path.GetTempPath(), pngFilename), FileMode.Open));

                // Create new sticker set
                if (UserMapping[userId] == null)
                {
                    UserMapping[userId] = $"Stickers_{Converter.GetRandomName(5)}_by_{BotName}";
                    Db.NewUser(userId, UserMapping[userId]);
                    _ = BotClient.CreateNewStickerSetAsync(userId, UserMapping[userId], "Сохраненки", newSticker, emoji);
                    Log.Information($"Created new sticker pack {UserMapping[userId]} for {userId}");
                    _ = BotClient.SendTextMessageAsync(
                            chatId: userId,
                            text: $"\u2705 Стикер успешно сохранен в [вот сюда](t.me/addstickers/{UserMapping[userId]})\\. Не забудь сохранить этот стикерпак\\.",
                            parseMode: ParseMode.MarkdownV2
                            );
                }

                // Add to existing sticker set
                else
                {
                    _ = BotClient.AddStickerToSetAsync(userId, UserMapping[userId], newSticker, emoji);
                    _ = BotClient.SendTextMessageAsync(userId, "\u2705 Стикер сохранен", ParseMode.Default, false, false, messageId);
                    Log.Information($"Added new sticker for {userId}");
                }
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"Bot.AddSticker({userId}, {pngFilename}): {ex.Message}");
                _ = BotClient.SendTextMessageAsync(userId, "\u274c Task failed successfully. Попробуй еще раз.", ParseMode.Default, false, false, messageId);
            }
        }
    }
}
