import pytest
from fastapi.testclient import TestClient
from main import app
from PIL import Image
import io

client = TestClient(app)

def create_test_image():
    # Create a simple image for testing
    image = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_compress_image():
    # Create a test image
    test_image = create_test_image()
    
    # Send the image to the API
    response = client.post(
        "/compress-image/",
        files={"file": ("test.jpg", test_image, "image/jpeg")}
    )
    
    # Check the response status code
    assert response.status_code == 200
    
    # Check the response data
    data = response.json()
    assert "original_size_kb" in data
    assert "compressed_size_kb" in data
    assert "compression_ratio" in data
    assert "download_url" in data
    
    # Check that the compressed size is less than the original size
    assert data["compressed_size_kb"] < data["original_size_kb"]
    
    # Check that the compression ratio is less than 1
    assert data["compression_ratio"] < 1

def test_download_image():
    # Create a test image
    test_image = create_test_image()
    
    # Send the image to the API
    response = client.post(
        "/compress-image/",
        files={"file": ("test.jpg", test_image, "image/jpeg")}
    )
    
    # Check the response status code
    assert response.status_code == 200
    
    # Get the download URL
    data = response.json()
    download_url = data["download_url"]
    
    # Download the compressed image
    download_response = client.get(download_url)
    
    # Check the download response status code
    assert download_response.status_code == 200
    
    # Check the content type of the downloaded image
    assert download_response.headers["content-type"] == "image/jpeg"

if __name__ == "__main__":
    pytest.main()