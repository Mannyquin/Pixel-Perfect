from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import tempfile
import requests
import logging

from predict import predict_attributes
from ai_generator import generate_avatar

from config import DEFAULT_STYLE

logger = logging.getLogger(__name__)

app = FastAPI(title="Avatar Generation App")



# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ROOT
@app.get("/")
def root():
    return {"status": "Avatar API is running"}


@app.get("/ping")
def ping():
    return {"message": "pong"}



# IMAGE PROXY
@app.get("/proxy-image")
def proxy_image(url: str):

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "image/*",
    }

    for attempt in range(2):

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=30,
            )

            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="image/png",
                )

            logger.warning(
                "Proxy returned status %s",
                response.status_code,
            )

        except requests.exceptions.ReadTimeout:

            logger.warning(
                "Proxy timeout (%d/2)",
                attempt + 1,
            )

        except Exception:

            logger.exception(
                "Proxy request failed."
            )

    raise HTTPException(
        status_code=504,
        detail="Image generation timed out.",
    )



# MAIN ENDPOINT (FIXED WITH STYLE SUPPORT)

@app.post("/generate")
async def generate(
    file: UploadFile = File(...),
    style: str = Form(DEFAULT_STYLE),
):

    if file.content_type not in (
        "image/jpeg",
        "image/png",
    ):
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported.",
        )

    image_bytes = await file.read()

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Maximum image size is 10 MB.",
        )

    suffix = (
        ".jpg"
        if file.content_type == "image/jpeg"
        else ".png"
    )

    tmp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as tmp:

            tmp.write(image_bytes)
            tmp_path = tmp.name

        logger.info(
            "Temporary image saved: %s",
            tmp_path,
        )

        prediction = predict_attributes(
            tmp_path
        )

        avatar = generate_avatar(
            prediction,
            style,
        )



        # If generate_avatar() returns AvatarResult
        if hasattr(avatar, "image_url"):

            return {
                "success": True,
                "image_url": avatar.image_url,
                "prediction": prediction,
                "prompt": avatar.prompt.prompt,
                "descriptors": avatar.prompt.descriptors,
                "style": avatar.prompt.style,
            }


        # If generate_avatar() returns URL string
        return {
            "success": True,
            "image_url": avatar,
            "prediction": prediction,
            "style": style,
        }

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Avatar generation failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Avatar generation failed.",
        )

    finally:

        if (
            tmp_path
            and os.path.exists(tmp_path)
        ):
            os.remove(tmp_path)

            logger.info(
                "Temporary file removed."
            )



static_dir = os.path.join(
    os.path.dirname(__file__),
    "static",
)

if os.path.exists(static_dir):

    app.mount(
        "/",
        StaticFiles(
            directory=static_dir,
            html=True,
        ),
        name="static",
    )