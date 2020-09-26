using Microsoft.Data.Sqlite;
using System.Collections.Generic;
using System.IO;
using Telegram.Bot.Requests;

namespace VorishkaBot
{
    public class DbHandler
    {
        private SqliteConnection sqlite;

        public DbHandler(string dbPath = "VorishkaBotDB")
        {
            bool newFile = false;
            if (!File.Exists(dbPath))
            {
                File.Create(dbPath);
                newFile = true;
            }

            string connectionString = "Data Source=VorishkaBotDB.sqlite";
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

        public void InsertUsers(int user_id, string set_name)
        {
            var query = sqlite.CreateCommand();
            query.CommandText = $"INSERT INTO users ('user_id', 'set_name') VALUES ({user_id}, '{set_name}')";
            query.ExecuteNonQuery();
        }
    }
}
