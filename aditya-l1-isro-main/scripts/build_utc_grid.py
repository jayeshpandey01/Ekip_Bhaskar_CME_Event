import dask.dataframe as dd
from minio import Minio
import os
from io import BytesIO
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

RAW_BUCKET = "cme-data-raw"
CURATED_BUCKET = "cme-data-curated"
SOURCES = ["ace_parent_directory"]

minio_client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def list_raw_files(prefix):
    return [
        obj.object_name
        for obj in minio_client.list_objects(RAW_BUCKET, prefix=prefix, recursive=True)
        if obj.object_name.endswith(".txt")
    ]

def parse_epam_file(buffer: BytesIO) -> pd.DataFrame:
    """
    Parse ACE EPAM-like file after skipping comments and reading structured data.
    """
    buffer.seek(0)
    lines = buffer.read().decode().splitlines()

    # Find the actual data line start
    for i, line in enumerate(lines):
        if line.strip().startswith("2001") or line.strip()[0:4].isdigit():
            data_start = i
            break
    else:
        raise ValueError("No data found")

    # Read from line i onwards using fixed space
    data = "\n".join(lines[data_start:])
    df = pd.read_csv(
        BytesIO(data.encode()),
        delim_whitespace=True,
        header=None,
        names=[
            "YR", "MO", "DA", "HHMM", "Julian_Day", "Sec_Day",
            "S_e", "Electron_38_53", "Electron_175_315",
            "S_p", "Proton_47_65", "Proton_112_187", "Proton_310_580",
            "Proton_761_1220", "Proton_060_1910", "Anisotropy_Ratio"
        ],
        engine="python",
        on_bad_lines="skip"
    )

    return df

def transform_and_store_parquet():
    if not minio_client.bucket_exists(CURATED_BUCKET):
        minio_client.make_bucket(CURATED_BUCKET)

    for source in SOURCES:
        print(f"\n🚀 Processing source: {source}")
        files = list_raw_files(source)

        for file_key in files:
            print(f"📦 Fetching: {file_key}")
            try:
                response = minio_client.get_object(RAW_BUCKET, file_key)
                buffer = BytesIO(response.read())
                df = parse_epam_file(buffer)

                if df.empty:
                    raise ValueError("Parsed DataFrame is empty")

                # Convert to pyarrow Table
                table = pa.Table.from_pandas(df)

                # Write to Parquet in memory
                parquet_buf = BytesIO()
                pq.write_table(table, parquet_buf)
                parquet_buf.seek(0)

                filename = os.path.basename(file_key).replace(".txt", ".parquet")

                # Extract year from filename (first 4 chars)
                year = filename[:4]
                if year not in [str(y) for y in range(2001, 2026)]:
                    year = "unknown_year"

                target_key = f"{source}/{year}/{filename}"

                minio_client.put_object(
                    bucket_name=CURATED_BUCKET,
                    object_name=target_key,
                    data=parquet_buf,
                    length=len(parquet_buf.getvalue())
                )

                print(f"✅ Uploaded: {target_key}")

            except Exception as e:
                print(f"❌ Error processing {file_key}: {e}")

if __name__ == "__main__":
    transform_and_store_parquet()
