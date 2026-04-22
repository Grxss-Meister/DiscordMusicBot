# 🎵 DiscordMusicBot

A simple Discord bot that plays music from YouTube directly in your voice channel.

---

## ✅ Requirements

- Python 3.14 
- A Discord Bot Token ([Get one here](https://discord.com/developers/applications))
- FFmpeg installed on your system ([Installation Tutorial](https://www.youtube.com/watch?v=JR36oH35Fgg&t=97s))

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/Grxss-Meister/DiscordMusicBot.git
cd DiscordMusicBot
```

**2. Install dependencies**
```bash
pip install discord.py yt-dlp python-dotenv
```

**3. Add your Bot Token**

Edit the file called `token.txt` inside the `src` folder and paste your Discord Bot Token in it:
```
YOUR_DISCORD_BOT_TOKEN_HERE
```

**4. Run the bot**

**Option A – VS Code (easy):**
Open `src/main.py` in VS Code and click the ▶️ Run button in the top right corner.

**Option B – Terminal:**
```bash
cd src
python main.py
```

---

## 🤖 How to get a Bot Token

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** and give it a name
3. Go to **Bot** → **Reset Token** and copy your token
4. Paste it into `src/token.txt`

---

## 📁 Project Structure

```
DiscordMusicBot/
└── src/
    ├── main.py
    ├── music_cog.py
    ├── help_cog.py
    └── token.txt        ← edit this yourself (not included!)
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE.md).
