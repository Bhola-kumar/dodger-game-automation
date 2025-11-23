from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
import config_generator
import dodger
import os
import uuid

app = FastAPI()

def remove_file(path: str):
    """
    Helper function to remove a file.
    Used as a background task to clean up video files after they are sent.
    """
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Successfully removed temp file: {path}")
    except Exception as e:
        print(f"Error removing file {path}: {e}")

@app.post("/generate_video")
async def generate_video(background_tasks: BackgroundTasks):
    """
    Generates a unique gameplay video.
    """
    # 1. Generate Config
    config = config_generator.generate_config()
    
    # 2. Define Output Path
    # We use /tmp because it is the standard temp location on Linux/Render.
    # It avoids permission issues and keeps your app directory clean.
    filename = f"video_{uuid.uuid4()}.mp4"
    output_path = os.path.join("/tmp", filename)
    
    # Ensure directory exists (just in case)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 3. Run Game
    # Note: In a high-traffic app, this blocking call should eventually 
    # be offloaded to a separate worker queue (like Celery), but this works for now.
    try:
        dodger.run_game(config, output_path)
    except Exception as e:
        return {"error": f"Game generation failed: {str(e)}"}
    
    # 4. Schedule Cleanup
    # This instructs FastAPI to run 'remove_file' AFTER the response is fully sent.
    background_tasks.add_task(remove_file, output_path)
    
    # 5. Return File
    return FileResponse(output_path, media_type="video/mp4", filename=filename)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Render sets the PORT env variable; default to 8080 if not set.
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)