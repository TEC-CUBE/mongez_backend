from PIL import Image
import base64
from io import BytesIO


def control_image_size(base64_string: str, limit: int):
    return ((len(base64_string) * (3 / 4)) - 1) / 1000 < limit


def create_thumbnail(base64_string: str, filename: str, size: tuple):
    try:
        with open(f"/tmp/{filename}", "wb") as f:
            f.write(base64.b64decode(base64_string))
        img = Image.open(f"/tmp/{filename}")
        buffer = BytesIO()
        img.thumbnail(size)
        try:
            img.save(buffer, format="JPEG")
        except OSError:
            img.save(buffer, format="PNG")
        myimage = buffer.getvalue()
        return base64.b64encode(myimage).decode("utf-8")
    except IOError:
        return "cannot create thumbnail for", filename


def optimize_image(base64_string: str, quality: int=20):
    buffer = BytesIO()
    image = Image.open(BytesIO(base64.b64decode(base64_string)))
    try:
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
    except OSError:
        image.save(buffer, format="PNG", quality=quality, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
