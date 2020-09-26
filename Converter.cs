using System;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace VorishkaBot
{
    public class Converter
    {
        public static string WebpToPng(string inputPath)
        {
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

            process = Process.Start(processInfo);

#if DEBUG
            Console.WriteLine(process.StandardOutput.ReadToEnd());
            Console.WriteLine(process.StandardError.ReadToEnd());
#endif

            process.WaitForExit();
            process.Close();

            File.Delete(inputPath);

            return outputPath;
        }

        public async static void DowndloadSticker(string savePath, string stickerId)
        {
            var telegramFile = await Program.Bot.GetFileAsync(stickerId);
            using (FileStream downloadFileStream = new FileStream(Path.Combine(Path.GetTempPath(), savePath), FileMode.Create))
            {
                try
                {
                    await Program.Bot.DownloadFileAsync(telegramFile.FilePath, downloadFileStream);
                } catch (Exception ex)
                {
                    // TODO: logging to sqlite
                    Console.WriteLine(ex.Message + "\\n" + ex.StackTrace);
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
