import os
from os import listdir
from os.path import isfile, join
from google.cloud import storage
import glob


def upload_folder_to_gcs(local_path, bucket, gcs_path):
    assert os.path.isdir(local_path)

    for local_file in glob.glob(local_path + "/**"):

        if not os.path.isfile(local_file):
            if not os.path.basename(local_file) in ignore_list:
                upload_folder_to_gcs(
                    local_file,
                    bucket,
                    gcs_path + "/" + os.path.basename(local_file),
                )
        else:
            remote_path = os.path.join(gcs_path, local_file[1 + len(local_path) :])
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)
            print(f'Uploaded {local_file} to "{bucketName}" bucket.')


if __name__ == "__main__":
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

    local_path = "."
    BUCKET_FOLDER_DIR = "2021"
    bucketName = "demo-2021"
    ignore_list = ["venv"]

    storage_client = storage.Client()

    print("ready setup")

    bucket = storage_client.get_bucket(bucketName)
    upload_folder_to_gcs(local_path, bucket, BUCKET_FOLDER_DIR)
