using Microsoft.Data.Sqlite;
using System;
using System.Collections.Generic;
using System.IO;

namespace VorishkaBot
{
    public class DbHandler
    {
        private SqliteConnection sqlite;

        public DbHandler(string dbName)
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
                                        set_name TEXT
                                    )";
                query.ExecuteNonQuery();
            }
        }

        public Dictionary<int, string> GetUsers()
        {
            var mapping = new Dictionary<int, string>();
            var query = sqlite.CreateCommand();
            query.CommandText = "SELECT * FROM users";
            var result = query.ExecuteReader();

            while (result.Read())
            {
                mapping[result.GetInt32(1)] = result.GetString(2);
            }

            return mapping;
        }

        public void NewUser(int user_id, string set_name)
        {
            var query = sqlite.CreateCommand();
            query.CommandText = $"INSERT INTO users ('user_id', 'set_name') VALUES ({user_id}, '{set_name}')";
            try
            {
                query.ExecuteNonQuery();
            } catch (SqliteException ex)
            {
                // TODO: error logging
                Console.WriteLine($"{ex.Message} (sqlite code: {ex.SqliteErrorCode})\n" + ex.StackTrace);
            }
        }
    }
}
