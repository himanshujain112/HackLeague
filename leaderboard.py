import sqlite3
import datetime

class DBManager:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.create_tables()

    def create_connection(self):
        """Establish and return a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()

                # Leaderboard Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS leaderboard (
                        user_id TEXT NOT NULL,
                        guild_id TEXT NOT NULL,
                        score INTEGER DEFAULT 0,
                        streak INTEGER DEFAULT 0,
                        last_submission TEXT DEFAULT NULL,
                        PRIMARY KEY (user_id, guild_id)
                    );
                """)

                # Challenge Index Table (Tracks index per guild and difficulty)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS challenge_index (
                        guild_id TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        challenge_index INTEGER DEFAULT 0,
                        PRIMARY KEY (guild_id, difficulty)
                    );
                """)

                # Solved Challenges Table (Prevents duplicate XP gains)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS solved_challenges (
                        user_id TEXT NOT NULL,
                        guild_id TEXT NOT NULL,
                        question_id INTEGER NOT NULL,
                        PRIMARY KEY (user_id, guild_id, question_id)
                    );
                """)

                conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")

    def update_xp(self, user_id: str, guild_id: str, xp: int):
        """Update a user's XP and streak, with streak bonuses."""
        try:
            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
            with self.create_connection() as conn:
                cursor = conn.cursor()
                
                # Fetch existing user record
                cursor.execute("SELECT score, streak, last_submission FROM leaderboard WHERE user_id = ? AND guild_id = ?", 
                               (user_id, guild_id))
                row = cursor.fetchone()
    
                # Default values
                new_score, new_streak, bonus_xp = xp, 1, 0
    
                if row is None:
                    # New user, insert initial data
                    cursor.execute(
                        "INSERT INTO leaderboard (user_id, guild_id, score, streak, last_submission) VALUES (?, ?, ?, ?, ?)",
                        (user_id, guild_id, xp, 1, now)
                    )
                else:
                    current_score, current_streak, last_submission = row
                    new_score = current_score + xp  # Base XP update
    
                    # Streak calculation
                    if last_submission:
                        last_submission_date = datetime.datetime.strptime(last_submission, "%Y-%m-%d %H:%M:%S")
                        if (datetime.datetime.utcnow() - last_submission_date).days == 1:
                            new_streak = current_streak + 1
                        else:
                            new_streak = 1
                    else:
                        new_streak = 1
    
                    # **Apply Streak Bonus**
                    streak_bonus = {3: 10, 7: 30, 30: 100}  # Streak bonus milestones
                    bonus_xp = streak_bonus.get(new_streak, 0)
                    new_score += bonus_xp
    
                    # Update user record
                    cursor.execute(
                        "UPDATE leaderboard SET score = ?, streak = ?, last_submission = ? WHERE user_id = ? AND guild_id = ?",
                        (new_score, new_streak, now, user_id, guild_id)
                    )
    
                conn.commit()
            return new_score, new_streak, bonus_xp  # Returning updated values
    
        except Exception as e:
            print(f"Error updating XP: {e}")
            return 0, 0, 0  # Default return in case of an error


    def get_leaderboard(self, guild_id: str, limit: int = 10):
        """Retrieve the top users for a given guild, ordered by score."""
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, score, streak FROM leaderboard WHERE guild_id = ? ORDER BY score DESC LIMIT ?",
                    (guild_id, limit)
                )
                rows = cursor.fetchall()
                return self.format_leaderboard(rows) if rows else "🏆 No leaderboard data yet!"
        except Exception as e:
            print(f"Error fetching leaderboard data: {e}")
            return "⚠️ Error retrieving leaderboard."

    def format_leaderboard(self, leaderboardData):
        """Format leaderboard results into a Discord-friendly string."""
        formattedData = "🏆 **Leaderboard** 🏆\n"
        for i, row in enumerate(leaderboardData):
            user_id, score, streak = row
            formattedData += f"{i+1}. <@{user_id}> - **{score} XP** | 🔥 Streak: {streak} Days\n"
        return formattedData

    def get_challenge_index(self, guild_id: str, difficulty: str):
        """Retrieve the last challenge index for a specific guild and difficulty."""
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT challenge_index FROM challenge_index WHERE guild_id = ? AND difficulty = ?", (guild_id, difficulty))
                result = cursor.fetchone()
                return result[0] if result else 0  # Default to 0 if no record exists
        except Exception as e:
            print(f"Error fetching challenge index: {e}")
            return 0

    def update_challenge_index(self, guild_id: str, difficulty: str, new_index: int):
        """Update the challenge index for a guild and difficulty level."""
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO challenge_index (guild_id, difficulty, challenge_index)
                    VALUES (?, ?, ?)
                    ON CONFLICT(guild_id, difficulty) DO UPDATE SET challenge_index = ?
                """, (guild_id, difficulty, new_index, new_index))
                conn.commit()
        except Exception as e:
            print(f"Error updating challenge index: {e}")

    def has_solved_question(self, user_id: str, guild_id: str, question_id: int) -> bool:
        """Check if a user has already solved a specific question."""
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM solved_challenges WHERE user_id = ? AND guild_id = ? AND question_id = ?",
                    (user_id, guild_id, question_id)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking solved question: {e}")
            return False

    def mark_question_as_solved(self, user_id: str, guild_id: str, question_id: int):
        """Mark a question as solved for a user so they can't resubmit."""
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO solved_challenges (user_id, guild_id, question_id) VALUES (?, ?, ?)",
                    (user_id, guild_id, question_id)
                )
                conn.commit()
        except Exception as e:
            print(f"Error marking question as solved: {e}")
