import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import base64
import os
import tempfile
from io import BytesIO
from PIL import Image

from pose_estimator import PoseEstimator

#FastAPI instance
app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #["http://localhost:8081", "http://192.168.1.138:8081"],  # Set to ["http://localhost:19006"] if you want to be more secure
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Instance of PoseEstimator class
pose = PoseEstimator()

#Each app.post relates to a different measurement accessed by the measuring page

@app.post("/tragusleft")
async def tragus_to_wall_left(request: Request):
    # Parse the base64 image from request
    body = await request.json()
    image_data = body.get('image')

    if not image_data:
        return {"status": "error", "message": "No image data received"}

    # Decode base64 -> bytes -> Pillow image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        tmp_path = tmp.name
        image.save(tmp_path, format='JPEG')

    result = pose.tragus_to_wall_left(tmp_path)
    os.remove(tmp_path)

    return {"status": "success", "result": result}

@app.post("/tragusright")
async def tragus_to_wall_right(request: Request):
    # Parse the base64 image from request
    body = await request.json()
    image_data = body.get('image')

    if not image_data:
        return {"status": "error", "message": "No image data received"}

    # Decode base64 -> bytes -> Pillow image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        tmp_path = tmp.name
        image.save(tmp_path, format='JPEG')

    result = pose.tragus_to_wall_right(tmp_path)

    os.remove(tmp_path)

    return {"status": "success", "result": result}

@app.post("/flexionleft")
async def side_flexion_left(request: Request):
    # Parse the base64 image from request
    body = await request.json()
    image_one_data = body.get('image1')
    image_two_data = body.get('image2')

    if not image_one_data or not image_two_data:
        return {"status": "error", "message": "No image data received"}

    # Decode base64 -> bytes -> Pillow image
    image_one_bytes = base64.b64decode(image_one_data)
    image_two_bytes = base64.b64decode(image_two_data)
    image_one = Image.open(BytesIO(image_one_bytes))
    image_two = Image.open(BytesIO(image_two_bytes))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp1:
        tmp1_path = tmp1.name
        image_one.save(tmp1_path, format='JPEG')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp2:
        tmp2_path = tmp2.name
        image_two.save(tmp2_path, format='JPEG')

    result = pose.side_flexion_left(tmp1_path, tmp2_path)

    os.remove(tmp1_path)
    os.remove(tmp2_path)

    return {"status": "success", "result": result}

@app.post("/rights")
async def side_flexion_right(request: Request):
    # Parse the base64 image from request
    body = await request.json()
    image_one_data = body.get('image1')
    image_two_data = body.get('image2')
    #print("Testing testing")

    if not image_one_data or not image_two_data:
        return {"status": "error", "message": "No image data received"}

    # Decode base64 -> bytes -> Pillow image
    image_one_bytes = base64.b64decode(image_one_data)
    image_two_bytes = base64.b64decode(image_two_data)
    image_one = Image.open(BytesIO(image_one_bytes))
    image_two = Image.open(BytesIO(image_two_bytes))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp1:
        tmp1_path = tmp1.name
        image_one.save(tmp1_path, format='JPEG')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp2:
        tmp2_path = tmp2.name
        image_two.save(tmp2_path, format='JPEG')

    result = pose.side_flexion_right(tmp1_path, tmp2_path)

    os.remove(tmp1_path)
    os.remove(tmp2_path)

    return {"status": "success", "result": result}

@app.post("/lumbar")
async def lumbar_flexion(request: Request):
    # Parse the base64 image from request
    body = await request.json()
    image_one_data = body.get('image1')
    image_two_data = body.get('image2')

    if not image_one_data or not image_two_data:
        return {"status": "error", "message": "No image data received"}

    # Decode base64 -> bytes -> Pillow image
    image_one_bytes = base64.b64decode(image_one_data)
    image_two_bytes = base64.b64decode(image_two_data)
    image_one = Image.open(BytesIO(image_one_bytes))
    image_two = Image.open(BytesIO(image_two_bytes))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp1:
        tmp1_path = tmp1.name
        image_one.save(tmp1_path, format='JPEG')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp2:
        tmp2_path = tmp2.name
        image_two.save(tmp2_path, format='JPEG')

    result = pose.lumbar_flexion(tmp1_path, tmp2_path)

    os.remove(tmp1_path)
    os.remove(tmp2_path)

    return {"status": "success", "result": result}

@app.post("/cervicalleft")
async def cervical_rotation_left(request: Request):
    # Parse the base64 image from request
    body = await request.json()
    image_one_data = body.get('image1')
    image_two_data = body.get('image2')

    if not image_one_data or not image_two_data:
        return {"status": "error", "message": "No image data received"}

    # Decode base64 -> bytes -> Pillow image
    image_one_bytes = base64.b64decode(image_one_data)
    image_two_bytes = base64.b64decode(image_two_data)
    image_one = Image.open(BytesIO(image_one_bytes))
    image_two = Image.open(BytesIO(image_two_bytes))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp1:
        tmp1_path = tmp1.name
        image_one.save(tmp1_path, format='JPEG')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp2:
        tmp2_path = tmp2.name
        image_two.save(tmp2_path, format='JPEG')

    result = pose.cervical_rotation_left(tmp1_path, tmp2_path)

    os.remove(tmp1_path)
    os.remove(tmp2_path)

    return {"status": "success", "result": result}

@app.post("/cright")
async def cervical_rotation_right(request: Request):
    # Parse the base64 image from request
    body = await request.json()
    image_one_data = body.get('image1')
    image_two_data = body.get('image2')

    if not image_one_data or not image_two_data:
        return {"status": "error", "message": "No image data received"}

    # Decode base64 -> bytes -> Pillow image
    image_one_bytes = base64.b64decode(image_one_data)
    image_two_bytes = base64.b64decode(image_two_data)
    image_one = Image.open(BytesIO(image_one_bytes))
    image_two = Image.open(BytesIO(image_two_bytes))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp1:
        tmp1_path = tmp1.name
        image_one.save(tmp1_path, format='JPEG')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp2:
        tmp2_path = tmp2.name
        image_two.save(tmp2_path, format='JPEG')

    result = pose.cervical_rotation_right(tmp1_path, tmp2_path)

    os.remove(tmp1_path)
    os.remove(tmp2_path)

    return {"status": "success", "result": result}


@app.post("/intermalleolar")
async def intermalleolar_distance(request: Request):
    # Parse the base64 image from request
    body = await request.json()
    image_data = body.get('image')

    if not image_data:
        return {"status": "error", "message": "No image data received"}

    # Decode base64 -> bytes -> Pillow image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        tmp_path = tmp.name
        image.save(tmp_path, format='JPEG')

    result = pose.intermalleolar_distance(tmp_path)

    os.remove(tmp_path)

    return {"status": "success", "result": result}

#Entry point
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

#uvicorn main:app --host 0.0.0.0 --port 8000
