using DotNetEnv;
using FluentScheduler;
using Serilog;
using Serilog.Events;
using System;
using System.IO;
using System.Reflection;

namespace VorishkaBot
{
    class Program
    {
        public static void Main()
        {
            var baseDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);

            // Load config
            var envPath = Path.Combine(baseDir, ".env");
            Console.WriteLine($"Loading {envPath}...");
            using (var stream = File.OpenRead(envPath))
            {
                Env.Load(stream);
            }

            // Initialize SQLite
            var sqliteName = Path.Combine(baseDir, Env.GetString("BOT_NAME"));
            Console.WriteLine($"Opening {sqliteName}.sqlite...");
            Db.Initialize(sqliteName);

            // Initialize logs
            Log.Logger = new LoggerConfiguration()
                .WriteTo.Console()
                .WriteTo.SQLite(sqliteDbPath: $"{sqliteName}.sqlite", tableName: "logs", restrictedToMinimumLevel: LogEventLevel.Information)
                .CreateLogger();

            // Fire up
            Bot.StartReceiving(Env.GetString("BOT_NAME"), Env.GetString("TOKEN"));
            Log.Information($"{Env.GetString("BOT_NAME")} has started");

            // Schedule tasks
            try
            {
                var registry = new Registry();
                registry.Schedule(() => { Converter.CleanTempFiles(); }).ToRunNow().AndEvery(1).Days();
                JobManager.Initialize(registry);
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"Could not schedule jobs");
                Environment.Exit(255);
            }

            // Manual break
            Console.WriteLine("Press any key to stop the bot");
            Console.ReadKey();
            Bot.BotClient.StopReceiving();
            Environment.Exit(0);
        }
    }
}
