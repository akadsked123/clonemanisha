from datetime import datetime
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageField, ImageFieldFile
from PIL import Image, UnidentifiedImageError

class ProfileImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        new_name = None  # Initialize new_name with a default value

        try:
            # Open the image using Pillow
            image = Image.open(content)

            # If the image has an alpha channel (RGBA), convert it to RGB
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # Crop the image to a square
            width, height = image.size
            new_size = min(width, height)
            left = (width - new_size) / 2
            top = (height - new_size) / 2
            right = (width + new_size) / 2
            bottom = (height + new_size) / 2
            image = image.crop((left, top, right, bottom))

            # Resize the image to 288x288
            image = image.resize((288, 288), Image.LANCZOS)

            # Save the processed image to an in-memory file with controlled quality
            temp_file = BytesIO()
            image.save(temp_file, format='JPEG', quality=85)  # Adjust quality to reduce file size
            temp_file.seek(0)

            # Check the size and adjust quality if necessary
            max_size = 5 * 1024 * 1024  # 5 MB
            quality = 85  # Initial quality
            while temp_file.tell() > max_size and quality > 10:  # Loop to reduce quality if file is too big
                temp_file = BytesIO()  # Reset the buffer
                quality -= 5  # Reduce quality
                image.save(temp_file, format='JPEG', quality=quality)
                temp_file.seek(0)

            # Generate the new filename
            user_id = getattr(self.instance, 'id')
            now = datetime.now()
            formatted_date = now.strftime("%d%m%Y")
            formatted_time = now.strftime("%H%M%S")
            new_name = f"{user_id}{formatted_date}{formatted_time}.jpg"

            # Create a ContentFile from the in-memory file
            content = ContentFile(temp_file.read(), new_name)

        except UnidentifiedImageError:
            # Handle the case where the image cannot be identified
            print("The uploaded file is not a valid image. Please upload a valid image file.")
            
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred while processing the image: {e}")

        # Ensure we only call super().save() if new_name and content are set
        if new_name and content:
            super().save(new_name, content, save)

class ProfileImageField(ImageField):
    attr_class = ProfileImageFieldFile

class CoverImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        new_name = None  # Initialize new_name with a default value

        try:
            # Open the image using Pillow
            image = Image.open(content)

            # If the image has an alpha channel (RGBA), convert it to RGB
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # Resize the image to cover the target dimensions while preserving aspect ratio
            target_width, target_height = 960, 540
            img_width, img_height = image.size

            # Calculate the scale to cover the target dimensions
            scale = max(target_width / img_width, target_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            # Resize image with the calculated dimensions
            image = image.resize((new_width, new_height), Image.LANCZOS)

            # Crop the image to the target dimensions
            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = (new_width + target_width) / 2
            bottom = (new_height + target_height) / 2
            image = image.crop((left, top, right, bottom))

            # Save the processed image to an in-memory file with controlled quality
            temp_file = BytesIO()
            quality = 85  # Initial quality
            while True:
                image.save(temp_file, format='JPEG', quality=quality)
                temp_file.seek(0)
                if temp_file.tell() <= 5 * 1024 * 1024 or quality <= 10:  # 5 MB limit
                    break
                quality -= 5  # Reduce quality

            # Generate the new filename
            user_id = getattr(self.instance, 'id', 'default')  # Use 'default' if user_id is not available
            now = datetime.now()
            formatted_date = now.strftime("%d%m%Y")
            formatted_time = now.strftime("%H%M%S")
            new_name = f"{user_id}{formatted_date}{formatted_time}.jpg"

            # Create a ContentFile from the in-memory file
            content = ContentFile(temp_file.read(), new_name)

        except UnidentifiedImageError:
            # Handle the case where the image cannot be identified
            print("The uploaded file is not a valid image. Please upload a valid image file.")
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred while processing the image: {e}")

        # Ensure we only call super().save() if new_name and content are set
        if new_name and content:
            super().save(new_name, content, save)

class CoverImageField(ImageField):
    attr_class = CoverImageFieldFile
