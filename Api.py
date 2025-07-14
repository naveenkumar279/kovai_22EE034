import requests
import json
import sys
from typing import Dict, Optional


class DriveApiClient:
    def __init__(self, base_url: str = "https://apihub.document360.io/v2/Drive", api_token: str = "", user_id: str = ""):
        self.base_url = base_url
        self.api_token = api_token
        self.user_id = user_id
        self.headers = {
            "Content-Type": "application/json",
            "api_token": self.api_token,
            "User-Id": self.user_id
        }

    def validate_token(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/Folders", headers=self.headers)
            return response.status_code in [200, 403]
        except requests.exceptions.RequestException:
            return False

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[requests.Response]:
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            print(f"Request to {url} returned status {response.status_code}")
            print("Response:", response.text)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None


class FolderManager:
    def __init__(self, api_client: DriveApiClient):
        self.api_client = api_client
        self.folder_id_storage = {}

    def create_folder(self):
        folder_name = input("Enter folder name: ").strip()
        if not folder_name:
            print("Folder name cannot be empty.")
            return

        request_data = {
            "title": folder_name
        }

        response = self.api_client._make_request("POST", "Folders", request_data)
        if response and response.status_code in [200, 201]:
            folder_data = response.json()
            if 'data' in folder_data:
                folder_id = folder_data['data'].get('id')
                print(f"Folder '{folder_name}' created with ID: {folder_id}")
                self.folder_id_storage[folder_name] = folder_id
        else:
            print("Failed to create folder.")

    def update_folder(self):
        if not self.folder_id_storage:
            print("No folders available.")
            return

        for name, fid in self.folder_id_storage.items():
            print(f"{name} (ID: {fid})")

        old_name = input("Enter folder name to rename: ").strip()
        if old_name not in self.folder_id_storage:
            print("Folder not found.")
            return

        new_name = input("Enter new folder name: ").strip()
        if not new_name:
            print("New name cannot be empty.")
            return

        folder_id = self.folder_id_storage[old_name]
        data = {"title": new_name}
        response = self.api_client._make_request("PUT", f"Folders/{folder_id}", data)

        if response and response.status_code == 200:
            del self.folder_id_storage[old_name]
            self.folder_id_storage[new_name] = folder_id
            print(f"Folder renamed to '{new_name}'.")
        else:
            print("Failed to update folder.")

    def delete_folder(self):
        if not self.folder_id_storage:
            print("No folders to delete.")
            return

        for name, fid in self.folder_id_storage.items():
            print(f"{name} (ID: {fid})")

        name = input("Enter folder name to delete: ").strip()
        folder_id = self.folder_id_storage.get(name)
        if not folder_id:
            print("Folder not found.")
            return

        confirm = input(f"Confirm delete '{name}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return

        response = self.api_client._make_request("DELETE", f"Folders/{folder_id}")
        if response and response.status_code in [200, 204]:
            del self.folder_id_storage[name]
            print(f"Folder '{name}' deleted.")
        else:
            print("Failed to delete folder.")


def main():
    print("Document360 Drive Folder Manager")
    api_token = input("Enter your API token: ").strip()
    user_id = input("Enter your User ID (usually your email): ").strip()

    if not api_token or not user_id:
        print("Both API token and User ID are required.")
        sys.exit(1)

    client = DriveApiClient(api_token=api_token, user_id=user_id)
    if not client.validate_token():
        print("Invalid API token or user ID.")
        sys.exit(1)

    manager = FolderManager(client)

    while True:
        print("\n1. Create Folder")
        print("2. Rename Folder")
        print("3. Delete Folder")
        print("4. Exit")

        choice = input("Choose an option (1–4): ").strip()

        if choice == '1':
            manager.create_folder()
        elif choice == '2':
            manager.update_folder()
        elif choice == '3':
            manager.delete_folder()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
