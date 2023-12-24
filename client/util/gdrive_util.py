import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from typing import List, Dict


def create_folder(drive_service,
                  folder_name: str,
                  parent_folder_id: str = None) -> str:
    """
    Create a folder in Google Drive and return its ID
    """

    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id] if parent_folder_id else []
    }

    new_folder = (drive_service.files()
                                   .create(body=folder_metadata,
                                           fields='id')
                                   .execute())

    print(f"Created Folder ID: {new_folder['id']}")
    return new_folder["id"]


def list_folder(drive_service,
                parent_folder_id=None) -> Dict:
    """
    List all folders and files in Google Drive
    """

    results = (drive_service.files()
                            .list(q=f"'{parent_folder_id}' in parents and trashed=false" if parent_folder_id else None,
                                  pageSize=1000,
                                  fields="nextPageToken, files(id, name, mimeType)")
                            .execute())
    items = results.get("files", [])

    if not items:
        print("No folders or files found in Google Drive.")
        return []
    else:
        print("Folders and files in Google Drive:")
        folder_dict = {}
        for item in items:
            folder_dict[item["name"]] = item["id"]
        return items


def download_file(drive_service,
                  file_id: str,
                  destination_path: str) -> None:
    """
    Download a file from Google Drive by its ID
    """

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, mode="wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")


def upload_file(drive_service,
                file_name: str,
                file_data: bytes,
                mimetype: str,
                parent_folder_id: str = None) -> str:
    """
    Upload a local file to Google Drive.
    If sucessful, return the file ID
    """
    try:
        file_metadata = {
                            "name": file_name,
                            "parents": [{"id": parent_folder_id, "kind": "drive#childList"}]
                        }
        media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype=mimetype)
        file = (drive_service.files()
                             .create(body=file_metadata, media_body=media, fields="id")
                             .execute()
        )
        print(f'File ID: {file.get("id")}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")


def delete_files(drive_service,
                 file_or_folder_ids: List) -> bool:
    """
    Delete a file or folder in Google Drive by ID
    """
    try:
        (drive_service.files()
                     .delete(fileId=file_or_folder_ids)
                     .execute())
        print(f"Successfully deleted file/folder with ID: {file_or_folder_ids}")
        return True
    except Exception as e:
        print(f"Error deleting file/folder with ID: {','.join(file_or_folder_ids)}")
        print(f"Error details: {str(e)}")
        return False


def get_gdrive_service(scopes: List,
                       credentials_file: str):
    """
    Get Google Drive service from credentials file and based on scopes
    """

    credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=scopes)
    return build("drive", "v3", credentials=credentials)

