# Dodger Game Automation API

Automated YouTube Shorts generator for Dodger gameplay videos.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file:
   ```env
   YT_REFRESH_TOKEN=your_refresh_token
   YT_CLIENT_ID=your_client_id
   YT_CLIENT_SECRET=your_client_secret
   YOUTUBE_PRIVACY_STATUS=private
   PORT=10000
   ```

3. **Start the server:**
   ```bash
   python main.py
   ```

4. **Test the routes:**
   ```bash
   python test_all_routes.py
   ```

## API Routes

- **POST `/generate_video`** - Generate a video file
- **POST `/upload_video`** - Upload an existing video to YouTube
- **POST `/generate_and_upload`** - Generate and upload in one request
- **GET `/health`** - Health check

## Testing

Run the comprehensive test script:
```bash
python test_all_routes.py
```

This will test all three routes and verify they're working correctly.

