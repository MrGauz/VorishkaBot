using Microsoft.Data.Sqlite;
using System;
using System.Collections.Generic;
using System.IO;

namespace VorishkaBot
{
    public class Db
    {
        private static SqliteConnection sqlite;

        public enum MsgTypes
        {
            INFO,
            DEBUG,
            ERROR
        }

        public static void Initialize(string dbName)
        {
            dbName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Data", dbName);

            bool newFile = false;
            if (!File.Exists(dbName + ".sqlite"))
            {
                newFile = true;
            }

            string connectionString = $"Data Source={dbName}.sqlite";
            sqlite = new SqliteConnection(connectionString);
            sqlite.Open();
            var query = sqlite.CreateCommand();

            if (newFile)
            {
                query.CommandText = @"CREATE TABLE users(
                                        id INTEGER PRIMARY KEY,
                                        user_id INT, 
                                        set_name TEXT,
                                        created_at DATETIME
                                    )";
                try
                {
                    query.ExecuteNonQuery();
                }
                catch (SqliteException ex)
                {
                    Console.WriteLine($"{ex.Message} (sqlite code: {ex.SqliteErrorCode})\n" + ex.StackTrace);
                    NewMsg(MsgTypes.ERROR, $"{ex.Message} (sqlite code: {ex.SqliteErrorCode})", 0, ex.StackTrace);
                }

                query.CommandText = @"CREATE TABLE logs(
                                        id INTEGER PRIMARY KEY,
                                        msg_type TEXT, 
                                        timestamp DATETIME,
                                        user INT,
                                        msg TEXT,
                                        stacktrace TEXT
                                    )";
                try
                {
                    query.ExecuteNonQuery();
                }
                catch (SqliteException ex)
                {
                    Console.WriteLine($"{ex.Message} (sqlite code: {ex.SqliteErrorCode})\n" + ex.StackTrace);
                    NewMsg(MsgTypes.ERROR, $"{ex.Message} (sqlite code: {ex.SqliteErrorCode})", 0, ex.StackTrace);
                }
            }
        }

        public static Dictionary<int, string> GetUsers()
        {
            var mapping = new Dictionary<int, string>();
            var query = sqlite.CreateCommand();
            query.CommandText = "SELECT * FROM users";
            try
            {
                var result = query.ExecuteReader();
                while (result.Read())
                {
                    mapping[result.GetInt32(1)] = result.GetString(2);
                }
            }
            catch (SqliteException ex)
            {
                Console.WriteLine($"{ex.Message} (sqlite code: {ex.SqliteErrorCode})\n" + ex.StackTrace);
                NewMsg(MsgTypes.ERROR, $"{ex.Message} (sqlite code: {ex.SqliteErrorCode})", 0, ex.StackTrace);
            }
            
            return mapping;
        }

        public static void NewUser(int userId, string set_name)
        {
            var query = sqlite.CreateCommand();
            query.CommandText = $"INSERT INTO users ('user_id', 'set_name', 'created_at') VALUES ({userId}, '{set_name}', '{DateTime.Now:yyyy-MM-dd HH:mm:ss}')";
            try
            {
                query.ExecuteNonQuery();
                NewMsg(Db.MsgTypes.INFO, $"Add new user to DB:{userId}", userId);
            } 
            catch (SqliteException ex)
            {
                Console.WriteLine($"{ex.Message} (sqlite code: {ex.SqliteErrorCode})\n" + ex.StackTrace);
                NewMsg(MsgTypes.ERROR, $"{ex.Message} (sqlite code: {ex.SqliteErrorCode})", userId, ex.StackTrace);
            }
        }

        public static void NewMsg(MsgTypes msgType, string msg, int userId, string stacktrace = "")
        {
            var query = sqlite.CreateCommand();
            query.CommandText = $"INSERT INTO logs ('msg_type', 'timestamp', 'user', 'msg', 'stacktrace') VALUES (" +
                $"{msgType}, " +
                $"'{DateTime.Now:yyyy-MM-dd HH:mm:ss}', " +
                $"'{userId}'," +
                $"'{msg}'," +
                $"'{stacktrace}'" +
                $")";
            try
            {
                query.ExecuteNonQuery();
            }
            catch (SqliteException ex)
            {
                Console.WriteLine($"{ex.Message} (sqlite code: {ex.SqliteErrorCode})\n" + ex.StackTrace);
                NewMsg(MsgTypes.ERROR, $"{ex.Message} (sqlite code: {ex.SqliteErrorCode})", 0, ex.StackTrace);
            }
        }
    }
}
