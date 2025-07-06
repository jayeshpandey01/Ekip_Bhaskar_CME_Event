# ~/Projects/space-weather-pipeline/scripts/upload_ace_only.py

import os
from minio import Minio
from minio.error import S3Error

# Local ACE folder
LOCAL_ACE_FOLDER = os.path.expanduser("~/Desktop/ace_parent_directory")


# MinIO settings
MINIO_BUCKET = "cme-data-raw"
MINIO_CLIENT = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def upload_ace():
    if not MINIO_CLIENT.bucket_exists(MINIO_BUCKET):
        MINIO_CLIENT.make_bucket(MINIO_BUCKET)
        print(f"📦 Created bucket: {MINIO_BUCKET}")

    for root, _, files in os.walk(LOCAL_ACE_FOLDER):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, LOCAL_ACE_FOLDER)
            object_name = f"ace_parent_directory/{relative_path}"

            with open(local_path, "rb") as f:
                MINIO_CLIENT.put_object(
                    bucket_name=MINIO_BUCKET,
                    object_name=object_name,
                    data=f,
                    length=os.path.getsize(local_path)
                )
            print(f"✅ Uploaded: {object_name}")

if __name__ == "__main__":
    upload_ace()
