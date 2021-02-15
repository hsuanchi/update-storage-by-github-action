import glob
import os
from os import listdir
from os.path import isfile, join

from google.cloud import storage


def upload_folder_to_gcs(local_path, bucket, gcs_path):
    assert os.path.isdir(local_path)

    for local_file in glob.glob(local_path + "/**"):

        if not os.path.basename(local_file) in ignore_list:
            if not os.path.isfile(local_file):
                upload_folder_to_gcs(
                    local_file,
                    bucket,
                    gcs_path + "/" + os.path.basename(local_file),
                )
            else:
                remote_path = os.path.join(gcs_path, local_file[1 + len(local_path) :])
                blob = bucket.blob(remote_path)
                blob.upload_from_filename(local_file)
                print(f'Uploaded {local_file} to "{bucket_name}" bucket.')


if __name__ == "__main__":
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"
    key_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    key_name = key_path.split("/")[-1]

    local_path = "."
    bucket_forder = ""
    bucket_name = "demo-2021"
    ignore_list = ["venv", key_name]

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    upload_folder_to_gcs(local_path, bucket, bucket_forder)
