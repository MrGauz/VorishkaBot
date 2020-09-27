using nQuant;
using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;

namespace VorishkaBot
{
    public class Converter
    {
        public static string WebpToPng(string inputPath)
        {
            // Convert WEBP to PNG
            string outputPath = GetRandomName() + ".png";
            ProcessStartInfo processInfo;
            Process process;

            processInfo = new ProcessStartInfo();
#if DEBUG
            processInfo.FileName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Tools", "ffmpeg.exe");
#else
            processInfo.FileName = Path.Combine("/usr/bin/ffmpeg");   
#endif
            processInfo.WorkingDirectory = Path.GetTempPath();
            processInfo.Arguments = $"-i {inputPath} {outputPath}";
            processInfo.CreateNoWindow = true;
            processInfo.UseShellExecute = false;
            processInfo.RedirectStandardError = true;
            processInfo.RedirectStandardOutput = true;

            try
            {
                process = Process.Start(processInfo);

#if DEBUG
                var stderr = process.StandardError.ReadToEnd();
                Db.NewMsg(Db.MsgTypes.DEBUG, stderr, 0);
#endif

                process.WaitForExit();
                process.Close();
                Db.NewMsg(Db.MsgTypes.INFO, $"Converted {inputPath} to {outputPath}", 0);

                File.Delete(inputPath);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, 0, ex.StackTrace);
            }

            // Reduce quality
            var quantizer = new WuQuantizer();
            var resizedPng = GetRandomName() + ".png";
            try
            {
                var bitmap = new Bitmap(Path.Combine(Path.GetTempPath(), outputPath));
                if (bitmap.PixelFormat != PixelFormat.Format32bppArgb)
                {
                    var bmp = new Bitmap(bitmap.Width, bitmap.Height, PixelFormat.Format32bppArgb);
                    using (var gr = Graphics.FromImage(bmp))
                        gr.DrawImage(bitmap, new Rectangle(0, 0, bitmap.Width, bitmap.Height));
                    bitmap.Dispose();
                    bitmap = bmp;
                }
                using (var quantized = quantizer.QuantizeImage(bitmap))
                {
                    quantized.Save(Path.Combine(Path.GetTempPath(), resizedPng), ImageFormat.Png);
                    Db.NewMsg(Db.MsgTypes.INFO, $"Reduced quality of {outputPath} to {resizedPng}", 0);
                }
                bitmap.Dispose();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, 0, ex.StackTrace);
            }

            File.Delete(Path.Combine(Path.GetTempPath(), outputPath));

            return resizedPng;
        }

        public async static void DowndloadSticker(string savePath, string stickerId, int userId)
        {
            var telegramFile = await Program.Bot.GetFileAsync(stickerId);
            using (FileStream downloadFileStream = new FileStream(Path.Combine(Path.GetTempPath(), savePath), FileMode.Create))
            {
                try
                {
                    await Program.Bot.DownloadFileAsync(telegramFile.FilePath, downloadFileStream);
                    Db.NewMsg(Db.MsgTypes.INFO, $"Downloaded {stickerId} to {savePath}", userId);
                } catch (Exception ex)
                {
                    Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                    Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, userId, ex.StackTrace);
                }
            }
        }

        public static string GetRandomName(int length = 8)
        {
            Random random = new Random();

            const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
            return new string(Enumerable.Repeat(chars, length).Select(s => s[random.Next(s.Length)]).ToArray());
        }
    }
}
