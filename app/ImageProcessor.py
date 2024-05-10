import os
from PIL import Image
from werkzeug.utils import secure_filename

class ImageProcessor:
    def __init__(self, upload_folder, output_folder, allowed_extensions=None):
        self.upload_folder = upload_folder
        self.output_folder = output_folder
        self.allowed_extensions = allowed_extensions or {'png', 'jpg', 'jpeg'}

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_file(self, file):
        filename = secure_filename(file.filename)
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        return file_path

    def split_image(self, image_path, n):
        img = Image.open(image_path)
        if n == 9:
            block_width = img.width // 3
            block_height = img.height // 3
            columns = rows = 3
        elif n == 6:
            block_width = img.width // 3
            block_height = img.height // 2
            columns = 3
            rows = 2
        else:
            block_width = img.width // 2
            block_height = img.height // 2
            columns = rows = 2

        prefix = os.path.basename(image_path).split('.')[0]
        extension = image_path.rsplit('.', 1)[1]

        # filename, image_path, piece_number
        fragments = []
        for i in range(rows):
            for j in range(columns):
                box = (j * block_width, i * block_height, (j + 1) * block_width, (i + 1) * block_height)
                cropped_img = img.crop(box)

                # Convert RGBA to RGB before saving as JPEG
                if cropped_img.mode == 'RGBA' and extension.lower() == 'jpg':
                    cropped_img = cropped_img.convert('RGB')
                
                filename = f"{prefix}-{i * columns + j + 1}.{extension}"
                path = os.path.join(self.output_folder, filename)
                cropped_img.save(path)
                fragments.append([filename, path, (i * columns + j + 1)])
        return fragments



