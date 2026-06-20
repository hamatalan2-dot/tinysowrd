import dropbox
from dotenv import load_dotenv
import sys
import os


load_dotenv()

# Your Dropbox API access token
ACCESS_TOKEN = os.getenv("TOKEN")

if not ACCESS_TOKEN:
    print("You forgot to add your Dropbox credentials to the `.env` file! Add it and try again!")
    sys.exit(1)

# Initialize the Dropbox client with a 15-minute timeout
dbx = dropbox.Dropbox(ACCESS_TOKEN, timeout=900)

print(
    "Get your token at https://www.dropbox.com/developers/apps and ensure you have the necessary permissions ticked on!"
)


def upload_file(file_path, dropbox_path):
    file_size = os.path.getsize(file_path)
    CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB chunks

    with open(file_path, "rb") as f:
        if file_size <= CHUNK_SIZE:
            dbx.files_upload(f.read(), dropbox_path)
        else:
            print(f"File is large ({file_size / (1024*1024):.2f} MB). Uploading in chunks...")
            upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
            cursor = dropbox.files.UploadSessionCursor(
                session_id=upload_session_start_result.session_id,
                offset=f.tell(),
            )
            commit = dropbox.files.CommitInfo(path=dropbox_path)

            while f.tell() < file_size:
                if (file_size - f.tell()) <= CHUNK_SIZE:
                    dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                else:
                    dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE), cursor)
                    cursor.offset = f.tell()

    print(f"File {file_path} uploaded to {dropbox_path} successfully.")

    # Generate a shared link
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)

    return shared_link_metadata.url


if __name__ == "__main__":
    upload_file("requirements.txt", "/requirements.txt")
