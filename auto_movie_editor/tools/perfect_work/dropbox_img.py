import dropbox
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from dotenv import load_dotenv
import time

load_dotenv()

class DropboxManager:
    def __init__(self, access_token=os.environ["DROPBOX_ACCESS_TOKEN"]):
        self.dbx = dropbox.Dropbox(access_token)
    
    def upload_image(self, local_path, dropbox_path):
        try:
            with open(local_path, "rb") as f:
                data = f.read()
            self.dbx.files_upload(data, dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
            return True
        except Exception as err:
            return False
            
    def delete_file(self, dropbox_path):
        try:
            self.dbx.files_delete_v2(dropbox_path)
            return True
        except Exception as err:
            return False

def upload_images_concurrently(manager, image_paths, dropbox_folder):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for local_path in image_paths:
            # Extract filename and form the destination path.
            filename = local_path.split("/")[-1]
            dropbox_path = f"{dropbox_folder}/{filename}"
            futures.append(executor.submit(manager.upload_image, local_path, dropbox_path))
        # Wait for all uploads to complete.
        for future in as_completed(futures):
            future.result()
            
    

# Example usage:
if __name__ == "__main__":
    manager = DropboxManager()

    dropbox_folder = "/temp_images"
    # Assume you have already created the directory in Dropbox.
    image_paths = ['output_no_text.jpg', 'output_no_metadata.jpg' ]  # List of 100 image paths
    # image_paths = [f"path/to/image_{i}.png" for i in range(1, 101)]  # List of 100 image paths

    upload_images_concurrently(manager, image_paths, dropbox_folder)
    print("Images uploaded successfully.")
    
    time.sleep(60)
    
    manager.delete_file(dropbox_folder)
    
