from azure.storage.blob import BlobServiceClient
from django.conf import settings

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient(
    account_url=f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=settings.AZURE_ACCOUNT_KEY,
)

# Upload File to Azure Blob Storage
def upload_file_to_azure(file, file_name):
    try:
        # Get the container client
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)
        # Upload the file
        blob_client = container_client.get_blob_client(file_name)
        blob_client.upload_blob(file, overwrite=True)
        # Return the file URL
        return blob_client.url
    except Exception as e:
        raise Exception(f"Failed to upload file: {str(e)}")

# Delete File from Azure Blob Storage
def delete_file_from_azure(file_name):
    try:
        # Get the container client
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)
        # Delete the file
        blob_client = container_client.get_blob_client(file_name)
        blob_client.delete_blob()
        return True
    except Exception as e:
        raise Exception(f"Failed to delete file: {str(e)}")