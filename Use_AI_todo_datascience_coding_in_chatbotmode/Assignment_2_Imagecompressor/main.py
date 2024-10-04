from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse,FileResponse
from pydantic import BaseModel
from PIL import Image
import io
from fastapi.staticfiles import StaticFiles
import uuid

app = FastAPI()

class ImageMetrics(BaseModel):
    original_size_kb: float
    compressed_size_kb: float
    compression_ratio: float
    download_url: str

# In-memory storage for compressed images
compressed_images = {}
@app.post("/compress-image/", response_model=ImageMetrics)
async def compress_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Only JPG and PNG are supported.")
    
    try:
        # Read the image file
        image = Image.open(file.file)
        
        # Calculate original size
        original_image_io = io.BytesIO()
        image.save(original_image_io, format=image.format)
        original_size = original_image_io.tell()
        original_size_kb = original_size / 1024
        
        # Compress the image
        compressed_image_io = io.BytesIO()
        image.save(compressed_image_io, format=image.format, quality=20)
        compressed_size = compressed_image_io.tell()
        compressed_size_kb = compressed_size / 1024
        
        # Calculate compression ratio
        compression_ratio = compressed_size / original_size
        
        # Generate a unique ID for the compressed image
        image_id = str(uuid.uuid4())
        compressed_image_io.seek(0)  # Reset the pointer to the beginning
        compressed_images[image_id] = compressed_image_io
        
        # Prepare response
        metrics = ImageMetrics(
            original_size_kb=original_size_kb,
            compressed_size_kb=compressed_size_kb,
            compression_ratio=compression_ratio,
            download_url=f"http://127.0.0.1:8000/download-image/{image_id}"
        )
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-image/{image_id}")
async def download_image(image_id: str):
    compressed_image_io = compressed_images.get(image_id)
    if not compressed_image_io:
        raise HTTPException(status_code=404, detail="Image not found")
    
    compressed_image_io.seek(0)
    return StreamingResponse(compressed_image_io, media_type="image/jpeg")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')     

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)       