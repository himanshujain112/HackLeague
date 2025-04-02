import sqlite3

class hackathonDB:
    def __init__(self, db_name="database/hackathon.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS hackathons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                tech_stack TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hackathon_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            FOREIGN KEY (hackathon_id) REFERENCES hackathon(id)
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hackathon_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            project_repo TEXT NOT NULL,
            FOREIGN KEY (hackathon_id) REFERENCES hackathon(id)
        )
        ''')
        # self.cursor.execute('''
        # CREATE TABLE IF NOT EXISTS votes (
        #     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     hackathon_id INTEGER NOT NULL,
        #     user_id INTEGER NOT NULL,
        #     vote TEXT NOT NULL,
        #     FOREIGN KEY (hackathon_id) REFERENCES hackathon(id)
        # )''')
        self.conn.commit()
    
    async def add_hackathon(self, guild_id, title, description, tech_stack, start_date, end_date):
        with self.conn:
            self.cursor.execute('''
                INSERT INTO hackathons (guild_id, title, description, tech_stack, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (guild_id, title, description, tech_stack, start_date, end_date,))
            self.conn.commit()

    async def get_hackathons(self, guild_id):
        with self.conn:
            self.cursor.execute('''
                SELECT * FROM hackathons WHERE guild_id = ?
            ''', (guild_id,))
            hackathons = self.cursor.fetchall()
            return hackathons
    
    async def add_submission(self, hackathon_id, user_id, project_repo):
        try:
            with self.conn:
                self.cursor.execute('''
                INSERT INTO submissions (hackathon_id, user_id, project_repo)
                VALUES (?,?,?)''', (hackathon_id, user_id, project_repo,))
                self.conn.commit()
                return True
        except Exception as e:
            return False
        
    async def get_submission(self, hackathon_id):
        with self.conn:
            self.cursor.execute('''
            SELECT * FROM submissions WHERE hackathon_id = ?
            ''', (hackathon_id,))
            projects = self.cursor.fetchall()
            return projects
    
    async def add_participant(self, hackathon_id, user_id, guild_id):
        with self.conn:
            self.cursor.execute('''
            INSERT INTO participants (hackathon_id, user_id, guild_id)
            VALUES (?,?,?)
        ''', (hackathon_id, user_id, guild_id,))
            self.conn.commit()
    
    async def get_participants(self, hackathon_id):
        with self.conn:
            self.cursor.execute('''
            SELECT * FROM participants WHERE hackathon_id = ?
            ''', (hackathon_id,))
            participants = self.cursor.fetchall()
            return participants
    
    async def get_hackathon_id(self, guild_id):
        with self.conn:
            self.cursor.execute('''SELECT id FROM hackathons WHERE guild_id = ? ORDER BY created_at DESC LIMIT 1
            ''', (guild_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None