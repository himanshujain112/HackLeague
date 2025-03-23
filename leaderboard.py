import sqlite3
import datetime

class DBManager:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.create_table()

    def create_connection(self):
        """Establish and return a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def create_table(self):
        try:
            """Create the leaderboard table if it doesn't exist."""
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leaderboard (
                    user_id TEXT NOT NULL,
                    guild_id TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    streak INTEGER DEFAULT 0,
                    last_submission TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                );
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"An error occurred while creating the leaderboard table: {e}")

    def update_xp(self, user_id: str, guild_id: str, xp: int):
        """
        Update a user's XP and streak.
        If the user does not exist for the guild, insert a new record.
        Otherwise, update the score and update the streak based on consecutive daily submissions.
        """
        try:
            conn = self.create_connection()
            cursor = conn.cursor()
            now = datetime.datetime.utcnow()

            # Check if the user exists in the given guild.
            cursor.execute(
                "SELECT score, streak, last_submission FROM leaderboard WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            row = cursor.fetchone()

            if row is None:
                # New entry: initialize score with xp, streak as 1, and record current time.
                cursor.execute(
                    "INSERT INTO leaderboard (user_id, guild_id, score, streak, last_submission) VALUES (?, ?, ?, ?, ?)",
                    (user_id, guild_id, xp, 1, now)
                )
            else:
                current_score, current_streak, last_submission = row
                new_score = current_score + xp

                # Check if the last submission was yesterday.
                if last_submission is not None:
                    last_submission_date = datetime.datetime.strptime(last_submission, "%Y-%m-%d %H:%M:%S.%f")
                    if (now - last_submission_date).days == 1:
                        new_streak = current_streak + 1
                    else:
                        new_streak = 1
                else:
                    new_streak = 1

                cursor.execute(
                    "UPDATE leaderboard SET score = ?, streak = ?, last_submission = ? WHERE user_id = ? AND guild_id = ?",
                    (new_score, new_streak, now, user_id, guild_id)
                )

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"An error occurred while updating XP: {e}")

    def formatLeaderboard(self, leaderboardData):
        formattedData = "🏆 **Leaderboard** 🏆\n"
        for i, row in enumerate(leaderboardData):
            user_id, score, streak = row
            formattedData += f"{i+1}. <@{user_id}> - Score: {score} | Streak: {streak} Days\n"
        return formattedData
    
    def get_leaderboard(self, guild_id: str, limit: int = 10):
        """
        Retrieve the top users for a given guild, ordered by score in descending order.
        Returns a list of tuples: (user_id, score, streak).
        """
        try:
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, score, streak FROM leaderboard WHERE guild_id = ? ORDER BY score DESC LIMIT ?",
                (guild_id, limit)
            )
            rows = cursor.fetchall()
            if not rows:
                return []
            conn.close()
            return self.formatLeaderboard(rows)
        except Exception as e:
            print(f"An error occurred while fetching leaderboard data: {e}")
            return []
    
   