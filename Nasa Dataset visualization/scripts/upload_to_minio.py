import os
from minio import Minio

LOCAL_ROOT = os.path.expanduser("~/Projects/space-weather-pipeline/data")
SOURCES = ["ace_parent_directory", "cactus_db", "kp_data", "aditya_l1"]
RAW_BUCKET = "cme-data-raw"

minio_client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def upload_raw():
    if not minio_client.bucket_exists(RAW_BUCKET):
        minio_client.make_bucket(RAW_BUCKET)

    for source in SOURCES:
        src_path = os.path.join(LOCAL_ROOT, source)
        for root, _, files in os.walk(src_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                relpath = os.path.relpath(fpath, src_path)
                object_name = f"{source}/{relpath}"

                with open(fpath, "rb") as f:
                    minio_client.put_object(
                        bucket_name=RAW_BUCKET,
                        object_name=object_name,
                        data=f,
                        length=os.path.getsize(fpath)
                    )
                print(f"✅ Uploaded {object_name} to {RAW_BUCKET}")

if __name__ == "__main__":
    upload_raw()
