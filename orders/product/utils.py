from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def crop_and_resize(image, size=(800, 800)):
    img = Image.open(image)

    # Crop the image to the center
    width, height = img.size
    aspect_ratio = size[0] / size[1]

    # Determine new dimensions for cropping
    if width / height > aspect_ratio:
        # Image is wider than the target aspect ratio
        new_width = int(aspect_ratio * height)
        left = (width - new_width) / 2
        right = (width + new_width) / 2
        img = img.crop((left, 0, right, height))
    else:
        # Image is taller than the target aspect ratio
        new_height = int(width / aspect_ratio)
        top = (height - new_height) / 2
        bottom = (height + new_height) / 2
        img = img.crop((0, top, width, bottom))

    # Resize the cropped image
    img.thumbnail(size, Image.ANTIALIAS)

    # Save the image to an in-memory file
    thumb_io = BytesIO()
    img.save(thumb_io, format='JPEG', quality=85)

    # Return a ContentFile for saving the image in the model
    return ContentFile(thumb_io.getvalue(), name=image.name)
