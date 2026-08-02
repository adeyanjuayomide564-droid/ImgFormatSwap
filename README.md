# ImgFormatSwapBot 🤖

A Telegram bot that converts images to different formats: JPEG, PNG, WEBP, BMP, TIFF, GIF, and PDF.

## 🎯 Features

- 📸 Convert images from Telegram photos and documents
- 🎨 Support for 7 different formats
- 🚀 Fast conversion with high quality (95% quality for JPEG)
- 🎞 Animated GIF support
- 📕 PDF conversion
- 🖱 Clean inline keyboard interface
- 💾 Session management

## 🛠️ Technologies Used

- Python 3.10+
- python-telegram-bot v20.0+
- Pillow (PIL) for image processing
- Deployed on Railway

## 🚀 Deployment on Railway

1. Fork this repository to your GitHub account
2. Go to [railway.app](https://railway.app) and sign in
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repository
5. Add environment variable:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
6. Railway will automatically deploy your bot!

## 🔧 Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ImgFormatSwapBot.git
   cd ImgFormatSwapBot
