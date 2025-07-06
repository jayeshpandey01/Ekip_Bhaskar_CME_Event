# scripts/upload_cactus_cme.py

import os
from minio import Minio

LOCAL_CACTUS_DIR = os.path.expanduser("~/Projects/space-weather-pipeline/data/cactus_db")
MINIO_BUCKET = "cme-data-raw"

minio_client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def upload_cactus_data():
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)

    for root, _, files in os.walk(LOCAL_CACTUS_DIR):
        for fname in files:
            local_path = os.path.join(root, fname)
            rel_path = os.path.relpath(local_path, LOCAL_CACTUS_DIR)
            minio_path = f"cactus_db/{rel_path}"

            with open(local_path, "rb") as f:
                minio_client.put_object(
                    bucket_name=MINIO_BUCKET,
                    object_name=minio_path,
                    data=f,
                    length=os.path.getsize(local_path),
                )
            print(f"✅ Uploaded {minio_path} to {MINIO_BUCKET}")

if __name__ == "__main__":
    upload_cactus_data()
