using DotNetEnv;
using System;
using System.Collections.Generic;
using System.Diagnostics;
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
        private static ITelegramBotClient Bot;
        private static String BotName;
        private static Dictionary<int, string> UserMapping;
        private static DbHandler db;

        public static void Main(string[] args)
        {
            // Init
            using (var stream = File.OpenRead(".env"))
            {
                Env.Load(stream);
                Bot = new TelegramBotClient(Env.GetString("TOKEN"));

                BotName = Env.GetString("BOT_NAME");
            }
            
            UserMapping = new Dictionary<int, string>();

            db = new DbHandler();
            UserMapping = db.GetUsers();

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
                // TODO: write logs to sqlite
                Console.WriteLine($"[INFO] {DateTime.Now:yyyy-MM-dd HH:mm:ss} - New user: {user_id}");
            }

            // Receive sticker
            if (e.Message.Type == MessageType.Sticker)
            {
                string emoji = e.Message.Sticker.Emoji;

                // Download WEBP sticker
                var telegramFile = await Bot.GetFileAsync(e.Message.Sticker.FileId);
                var savePath = Path.GetRandomFileName() + ".webp";
                using (FileStream downloadFileStream = new FileStream(Path.Combine(Path.GetTempPath(), savePath), FileMode.Create))
                {
                    // TODO: add try-catch on awaits
                    await Bot.DownloadFileAsync(telegramFile.FilePath, downloadFileStream);
                }

                // Convert sticker to PNG
                var convertPath = ConvertToPng(savePath);
                Console.WriteLine($"[INFO] {DateTime.Now:yyyy-MM-dd HH:mm:ss} - Downloaded and converted sticker: {e.Message.Sticker.FileId} (for {user_id})");

                InputOnlineFile newSticker = new InputOnlineFile(new FileStream(Path.Combine(Path.GetTempPath(), convertPath), FileMode.Open));

                // Create new sticker set
                if (UserMapping[user_id] == null)
                {
                    UserMapping[user_id] = "sohranenki_" + DateTime.Now.Ticks.ToString().Substring(8, 7) + "_by_" + BotName;
                    db.InsertUsers(user_id, UserMapping[user_id]);
                    await Bot.CreateNewStickerSetAsync(user_id, UserMapping[user_id], "Сохраненки", newSticker, emoji);
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
                        Console.WriteLine($"[ERROR] {DateTime.Now:yyyy-MM-dd HH:mm:ss} - Could not add sticker to set ({user_id})");
                        Console.WriteLine(ex.Message);
                        Console.WriteLine(ex.StackTrace);
                        await Bot.ForwardMessageAsync(user_id, user_id, e.Message.MessageId);
                    }
                }

                // Clean up
                //File.Delete(Path.Combine(Path.GetTempPath(), savePath));
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

        public static string ConvertToPng(string inputFile)
        {
            string outputFile = Path.GetRandomFileName() + ".png";
            ProcessStartInfo processInfo;
            Process process;

            processInfo = new ProcessStartInfo();
#if DEBUG
            processInfo.FileName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Tools", "ffmpeg.exe");
#else
            processInfo.FileName = Path.Combine("/usr/bin/ffmpeg");            
#endif
            processInfo.WorkingDirectory = Path.GetTempPath();
            processInfo.Arguments = $"-i {inputFile} {outputFile}";
            processInfo.CreateNoWindow = true;
            processInfo.UseShellExecute = false;
            processInfo.RedirectStandardError = true;
            processInfo.RedirectStandardOutput = true;

            process = Process.Start(processInfo);

#if DEBUG
            Console.WriteLine(process.StandardOutput.ReadToEnd());
            Console.WriteLine(process.StandardError.ReadToEnd());
#endif

            process.WaitForExit();
            process.Close();

            return outputFile;
        }
    }
}
