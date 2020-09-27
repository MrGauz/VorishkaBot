using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace VorishkaBot
{
    public class Converter
    {
        public static string ToPng(string inputFilename)
        {
            string outputFilename = GetRandomName() + ".png";
            ProcessStartInfo processInfo;
            Process process;

            processInfo = new ProcessStartInfo();
#if DEBUG
            processInfo.FileName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Tools", "ffmpeg.exe");
#else
            processInfo.FileName = Path.Combine("/usr/bin/ffmpeg");   
#endif
            processInfo.WorkingDirectory = Path.GetTempPath();
            processInfo.Arguments = $"-i {inputFilename} {outputFilename}";
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
                Db.NewMsg(Db.MsgTypes.INFO, $"Converted {inputFilename} to {outputFilename}", 0);

                File.Delete(inputFilename);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, 0, ex.StackTrace);
            }

            File.Delete(Path.Combine(Path.GetTempPath(), inputFilename));

            return outputFilename;
        }

        public static string QuantifyPng(string inputFilename)
        {
            var outputFilename = Path.GetFileNameWithoutExtension(inputFilename) + "_quant.png";
            ProcessStartInfo processInfo;
            Process process;

            processInfo = new ProcessStartInfo();
#if DEBUG
            processInfo.FileName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Tools", "pngquant.exe");
#else
            processInfo.FileName = Path.Combine("/usr/bin/pngquant");   
#endif
            processInfo.WorkingDirectory = Path.GetTempPath();
            processInfo.Arguments = $"{inputFilename} --ext _quant.png";
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
                Db.NewMsg(Db.MsgTypes.INFO, $"Reduce bit depth from 32 to 8 for {inputFilename} (--> {outputFilename})", 0);

                File.Delete(inputFilename);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, 0, ex.StackTrace);
            }

            //File.Delete(Path.Combine(Path.GetTempPath(), inputFilename));

            return outputFilename;
        }

        public static string ResizePng(string inputFilename)
        {
            var outputFilename = GetRandomName() + ".png";            
            ProcessStartInfo processInfo;
            Process process;

            processInfo = new ProcessStartInfo();
#if DEBUG
            processInfo.FileName = @"C:\Program Files\ImageMagick-7.0.10-Q16-HDRI\magick.exe";
            processInfo.WorkingDirectory = Path.GetTempPath();
            processInfo.Arguments = $"{inputFilename} -resize 512x512 {outputFilename}";
#else
            processInfo.FileName = Path.Combine("/usr/bin/convert");   
            processInfo.WorkingDirectory = Path.GetTempPath();
            processInfo.Arguments = $"{inputFilename} -resize 512x512 {outputFilename}";
#endif

            processInfo.CreateNoWindow = true;
            processInfo.UseShellExecute = false;
            processInfo.RedirectStandardError = true;
            processInfo.RedirectStandardOutput = true;

            try
            {
                process = Process.Start(processInfo);

                process.WaitForExit();
                process.Close();
                Db.NewMsg(Db.MsgTypes.INFO, $"Resize {inputFilename} to {outputFilename}", 0);

                File.Delete(inputFilename);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message + "\n" + ex.StackTrace);
                Db.NewMsg(Db.MsgTypes.ERROR, ex.Message, 0, ex.StackTrace);
            }

            File.Delete(Path.Combine(Path.GetTempPath(), inputFilename));

            return outputFilename;
        }

        public async static Task DownloadTgFile(string saveFilename, string fileId, int userId)
        {
            var telegramFile = await Program.Bot.GetFileAsync(fileId);
            using (FileStream downloadFileStream = new FileStream(Path.Combine(Path.GetTempPath(), saveFilename), FileMode.Create))
            {
                try
                {
                    await Program.Bot.DownloadFileAsync(telegramFile.FilePath, downloadFileStream);
                    Db.NewMsg(Db.MsgTypes.INFO, $"Downloaded {fileId} to {saveFilename}", userId);
                } 
                catch (Exception ex)
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
