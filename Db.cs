using Microsoft.Data.Sqlite;
using Serilog;
using System;
using System.Collections.Generic;
using System.IO;

namespace VorishkaBot
{
    public class Db
    {
        private static SqliteConnection sqlite;

        public static void Initialize(string dbName)
        {
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
                                        created_at DATETIME,
                                        deleted_at DATETIME
                                    );";
                try
                {
                    query.ExecuteNonQuery();
                }
                catch (SqliteException ex)
                {
                    Log.Error(ex, $"Db.GetUsers(): {ex.Message} (sqlite code: {ex.SqliteErrorCode})");
                }
            }
        }

        public static Dictionary<int, string> GetUsers()
        {
            var mapping = new Dictionary<int, string>();
            var query = sqlite.CreateCommand();
            query.CommandText = "SELECT * FROM users WHERE deleted_at IS NULL;";
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
                Log.Error(ex, $"Db.GetUsers(): {ex.Message} (sqlite code: {ex.SqliteErrorCode})");
            }

            return mapping;
        }

        public static void NewUser(int userId, string set_name)
        {
            var query = sqlite.CreateCommand();
            query.CommandText = $"INSERT INTO users ('user_id', 'set_name', 'created_at') VALUES ({userId}, '{set_name}', '{DateTime.Now:yyyy-MM-dd HH:mm:ss}');";
            try
            {
                query.ExecuteNonQuery();
                Log.Information($"Add new user to DB: {userId}");
            }
            catch (SqliteException ex)
            {
                Log.Error(ex, $"Db.NewUser({userId}, {set_name}): {ex.Message} (sqlite code: {ex.SqliteErrorCode})");
            }
        }

        public static void DeleteUser(int userId)
        {
            var query = sqlite.CreateCommand();
            query.CommandText = $"UPDATE users SET deleted_at = '{DateTime.Now:yyyy-MM-dd HH:mm:ss}' WHERE user_id = {userId};";
            try
            {
                query.ExecuteNonQuery();
                Log.Information($"Remove user from DB: {userId}");
            }
            catch (SqliteException ex)
            {
                Log.Error(ex, $"Db.DeleteUser({userId}): {ex.Message} (sqlite code: {ex.SqliteErrorCode})");
            }
        }
    }
}
