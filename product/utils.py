from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

# Image cropping and resizing function
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
    img = img.resize(size, Image.Resampling.LANCZOS)

    # Save the image to an in-memory file
    thumb_io = BytesIO()
    img.save(thumb_io, format='JPEG', quality=85)

    # Return a ContentFile for saving the image in the model
    return ContentFile(thumb_io.getvalue(), name=f"{image.name.split('.')[0]}.jpg")


# Image validation function
def validate_image(image):
    # Validate image type
    valid_image_formats = ['image/jpeg', 'image/png', 'image/jpg']  # Add more if needed
    if image.content_type not in valid_image_formats:
        raise ValidationError("Invalid image format. Please upload a JPEG or PNG image.")

    # Validate image size (max 5 MB, you can adjust this size as needed)
    max_size = 5 * 1024 * 1024  # 5 MB
    if image.size > max_size:
        raise ValidationError("Image file is too large. The maximum size allowed is 5MB.")
