# HackLeague - Discord Bot

HackLeague is an AI-powered coding judge and leaderboard bot designed for Discord servers. It enables users to participate in daily coding challenges, submit solutions, and earn XP to climb the leaderboard. The bot also provides AI-driven feedback to help users improve their coding skills.

---

## Features

- 🚀 **Daily Coding Challenges**: Generate coding challenges of varying difficulty (`easy`, `medium`, `hard`) for users to solve.
- 🤖 **AI-Powered Code Validation**: Validate user submissions using AI and provide structured feedback.
- 🏆 **Leaderboard System**: Track user XP and streaks to rank participants in the server.
- 🔥 **Streak Rewards**: Encourage consistent participation with streak bonuses.
- 🎭 **Role Assignment**: Automatically assign roles based on XP thresholds.
- 📊 **User-Friendly Commands**: Intuitive commands for interacting with the bot.

---

## Installation

### Prerequisites

- Python 3.10 or higher
- A Discord bot token
- A `.env` file with the following variables:
  ```
  DISCORD_TOKEN=<your_discord_bot_token>
  GEMINI_KEY=<your_gemini_api_key>
  ```

### Steps

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd HackLeague
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the `.env` file:

   - Create a `.env` file in the root directory.
   - Add your `DISCORD_TOKEN` and `GEMINI_KEY` as shown above.

4. Run the bot:
   ```bash
   python bot.py
   ```

---

## Commands

### General Commands

- `/ping`: Check if the bot is online and responsive.
- `/help`: Display a list of available commands.

### Challenge Commands

- `/start_challenge <difficulty>`: Generate a daily coding challenge (`easy`, `medium`, `hard`).

### Submission Commands

- `/submit <question_id> <code>`: Submit your solution for validation.

---

## XP Thresholds for Roles

| XP   | Role                |
| ---- | ------------------- |
| 100  | Beginner Coder      |
| 300  | Intermediate Coder  |
| 700  | Elite Coder         |
| 1500 | HackLeague Champion |
| 3000 | HackLeague Legend   |

---

## Contributing

We welcome contributions to HackLeague! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

## Support

If you encounter any issues or have questions, feel free to open an issue in the repository or contact the project maintainer.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

- **Discord.py** for the bot framework.
- **Google GenAI** for AI-powered validation.
- All contributors and users for their support and feedback.
