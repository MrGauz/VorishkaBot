# VorishkaBot aka Воришка стикеров

> 🤖 Here's [a link to the bot](https://t.me/VorishkaStickersBot). It talks to you in Russian.

This Telegram bot saves your favorite stickers to one pack, so you don't have to spend half a day searching for your favorite meme among dozens of sticker packs you've saved. An upgraded version of pinned "Favourite stickers" if you will.

**What can the chatbot do?**
- ✅ Save static stickers
- ✅ Make stickers from images

**What can't the chatbot do?**
- ❌ Save animated stickers
- ❌ Delete stickers from a sticker pack or change their order

## ⚒️ Run it yourself
1. Clone this repository:
   - ``git clone https://github.com/MrGauz/VorishkaBot.git``
2. Create ``.env`` with the config (make a copy of ``.env.example`` and populate it)
3. Install [.NET 6.0 Runtime](https://dotnet.microsoft.com/en-us/download/dotnet/6.0)
4. Install [ffmpeg](https://www.ffmpeg.org/download.html) for converting images
    - Make sure ``ffmpeg`` is added to PATH
5. Install [ImageMagick](https://imagemagick.org/script/download.php)
    - Make sure ``magick`` (Win) or ``convert`` (*nix) is added to PATH
6. Install [pngquant](https://pngquant.org/)
    - Make sure ``pngquant`` is added to PATH
7. Build the project; compiled code can be found in ``bin/Release/net6.0/``:
   - ``dotnet build -c Release``
   - Make sure .env was copied to the folder with compiled code.
8. Run your bot:
   - ``dotnet bin/Release/net6.0/BirthdaysBot.dll``
