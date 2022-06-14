using Serilog;
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

namespace VorishkaBot
{
    public class Converter
    {
        public static string ToPng(string inputFilename)
        {
            string outputFilename = Path.Combine(Path.GetTempPath(), $"VorishkaBot_{GetRandomName()}.png");
            
            var processInfo = new ProcessStartInfo
            {
                FileName = "ffmpeg",
                Arguments = $"-i {inputFilename} {outputFilename}",
                CreateNoWindow = true,
                UseShellExecute = false,
                RedirectStandardError = true,
                RedirectStandardOutput = true
            };

            try
            {
                var process = Process.Start(processInfo);

                var stderr = process.StandardError.ReadToEnd();
                Log.Debug(stderr);

                process.WaitForExit();
                process.Close();
                Log.Information($"Converted {inputFilename} to {outputFilename}");
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"Converter.ToPng({inputFilename}): {ex.Message}");
            }

            return outputFilename;
        }

        public static string QuantifyPng(string inputFilename)
        {
            var outputFilename = Path.Combine(Path.GetTempPath(), Path.GetFileNameWithoutExtension(inputFilename) + "_quant.png");

            var processInfo = new ProcessStartInfo
            {
                FileName = "pngquant",
                Arguments = $"{inputFilename} --ext _quant.png",
                CreateNoWindow = true,
                UseShellExecute = false,
                RedirectStandardError = true,
                RedirectStandardOutput = true
            };

            try
            {
                var process = Process.Start(processInfo);

                var stderr = process.StandardError.ReadToEnd();
                Log.Debug(stderr);

                process.WaitForExit();
                process.Close();
                Log.Information($"Reduce bit depth from 32 to 8 for {inputFilename} (--> {outputFilename})");
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"Converter.QuantifyPng({inputFilename}): {ex.Message}");
            }

            return outputFilename;
        }

        public static string ResizePng(string inputFilename)
        {
            var outputFilename = Path.Combine(Path.GetTempPath(), $"VorishkaBot_{GetRandomName()}.png");
            string magickExecutable;
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
            {
                magickExecutable = "convert";
            }
            else
            {
                magickExecutable = "magick";
            }

            var processInfo = new ProcessStartInfo
            {
                FileName = magickExecutable,
                Arguments = $"{inputFilename} -resize 512x512 {outputFilename}",
                CreateNoWindow = true,
                UseShellExecute = false,
                RedirectStandardError = true,
                RedirectStandardOutput = true
            };

            try
            {
                var process = Process.Start(processInfo);

                process.WaitForExit();
                process.Close();
                Log.Information($"Resized {inputFilename} to {outputFilename}");
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"Converter.ResizePng({inputFilename}): {ex.Message}");
            }

            return outputFilename;
        }

        public async static Task DownloadTgFile(string saveFilename, string fileId, int userId)
        {
            var telegramFile = await Bot.BotClient.GetFileAsync(fileId);
            using var downloadFileStream = new FileStream(saveFilename, FileMode.Create);
            try
            {
                await Bot.BotClient.DownloadFileAsync(telegramFile.FilePath, downloadFileStream);
                Log.Information($"Downloaded {fileId} to {saveFilename} (userId: {userId})");
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"Converter.DownloadTgFile({saveFilename}, {fileId}, {userId}): {ex.Message}");
            }
        }

        public static string GetRandomName(int length = 8)
        {
            var random = new Random();
            const string chars = "WATCHOUTFORYOURSTICKERS";
            return new string(Enumerable.Repeat(chars, length).Select(s => s[random.Next(s.Length)]).ToArray());
        }

        public static void CleanTempFiles()
        {
            try
            {
                Log.Information($"Deleting temp files older than 30 days has started");

                foreach (string file in Directory.EnumerateFiles(Path.GetTempPath(), "VorishkaBot_*"))
                {
                    var fileInfo = new FileInfo(file);
                    if (fileInfo.LastWriteTime < DateTime.Now.AddDays(-30))
                    {
                        File.Delete(file);
                        Log.Information($"Deleted {file}");
                    }
                }
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"Converter.CleanTempFiles(): {ex.Message}");
            }
        }
    }
}
