import os
import sys
import datetime
import io
import subprocess
# Google Authentication libraries for security and login flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
# Google API client for making the actual Drive requests
from googleapiclient.discovery import build
# File handlers for uploading and downloading media content
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

def get_base_path():
    """
    Determines the base path of the application.
    - If running as a compiled EXE (Frozen), uses sys.executable.
    - If running as a script, uses the file path.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
    
def get_config_path(filename):
    """
    Constructs the full path for a file inside the 'config' folder.
    """
    return os.path.join(get_base_path(), 'config', filename)

# Add 'config' folder to system path to allow importing db_config
config_dir = os.path.join(get_base_path(), 'config')
sys.path.append(config_dir)

try:
    import db_config
except ImportError:
    print("❌ Error: Could not find 'db_config.py' inside 'config' folder.")
    sys.exit(1)

# Define paths for Google Auth files using the config function
CREDENTIALS_FILE = get_config_path('credentials.json')
TOKEN_FILE = get_config_path('token.json')

# Database Credentials
DB_HOST = db_config.DB_HOST
DB_USER = db_config.DB_USER
DB_PASSWORD = db_config.DB_PASSWORD
DB_NAME = db_config.DB_NAME

# MySQL Tools Paths
# These tools are needed to export/import the database.
MYSQL_DUMP_PATH = r"C:\xampp\mysql\bin\mysqldump.exe"
MYSQL_CMD_PATH = r"C:\xampp\mysql\bin\mysql.exe"

# Constant: Define the security scope. This limits access only to files created by this specific application.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive():
    """
    Purpose: Handles user authentication using OAuth 2.0 flow.
    It manages the token lifecycle (check, refresh, save).
    Returns the ready-to-use Google Drive service object.
    """
    creds = None
    
    # 1. Check for the saved token (persisting the user's login session)
    if os.path.exists(TOKEN_FILE):
        # If the file exists, load the credentials from the stored JSON file
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # 2. If no valid token exists, initiate the login process
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # If token is expired but refresh token is available, try to renew it automatically
            try:
                creds.refresh(Request())
            except Exception:
                # If refresh fails (e.g., Google revoked the token), delete the bad token
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                # Recursively call the function to force a full re-login via browser
                return authenticate_google_drive()
        else:
            # Check to ensure the application's 'ID Card' is present before starting browser flow
            if not os.path.exists(CREDENTIALS_FILE):
                print("❌ Error: 'credentials.json' file not found!")
                print("HINT: Place the downloaded JSON file in the project root.")
                return None

            # Start the interactive flow which opens the user's web browser for login
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            try:
              creds = flow.run_local_server(port=0 , timeout_seconds=60) # port=0 finds a free port automatically
            except Exception as e:
              print(f"❌ Authentication Failed or Cancelled: {e}")
              return None  
        
        # 3. Save the new credentials/token for future sessions (avoids login next time)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    # Build and return the Google Drive API service object (v3)
    return build('drive', 'v3', credentials=creds)

def create_backup():
    """
    Exports the local MySQL database to a .sql file and uploads it to Google Drive.
    """
    try:
        # 1. Define backup folder path relative to the script
        base_dir = get_base_path()
        backup_folder = os.path.join(base_dir, 'backups')
        
        print(f"📍 Script Path: {base_dir}")
        
        # 2. Create folder if missing
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
            print(f"📁 Created backup folder at: {backup_folder}")

        # Get the authenticated service object
        service = authenticate_google_drive()
        if not service:
            return False # Exit if authentication failed
        
        # 1. Prepare the unique, timestamped backup name for versioning
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = os.path.join(backup_folder, f"ims_backup_{timestamp}.sql")
        
        print("⏳ Exporting database from MySQL...")
        
        # Step 3: Run 'mysqldump' command to export data
        # We open the file in write mode ('w') to save the output of mysqldump
        with open(backup_filename, 'w') as f:
            args = [MYSQL_DUMP_PATH, '-u', DB_USER, f'-h{DB_HOST}', DB_NAME]
            if DB_PASSWORD:
                args.append(f'-p{DB_PASSWORD}')
                
            # subprocess runs the external command line tool
            process = subprocess.Popen(args, stdout=f)
            process.wait() # Wait until the dump is complete
            
        # Check if mysqldump was successful (return code 0 means success)
        if process.returncode != 0:
            print("❌ Error: mysqldump failed. Check paths and credentials.")
            return False

        # Define the file's properties on Google Drive
        clean_name = os.path.basename(backup_filename)
        file_metadata = {'name': clean_name}
        
        # Prepare the file content for upload (mimetype application/octet-stream is for generic binary data)
        media = MediaFileUpload(backup_filename, mimetype='application/x-sql')
        
        print(f"⏳ Uploading backup: {backup_filename} ...")
        
        # 2. Execute the API command to create the file
        file = service.files().create(
            body=file_metadata,      # Metadata includes the unique filename
            media_body=media,        # The actual database file content
            fields='id'              # Only request the file ID back for confirmation
        ).execute()
        
        print(f"✅ Backup successful! (File ID: {file.get('id')})")

            
        return True
    
    except Exception as e:
        # Catch any errors (Network, API server, etc.) and prevent program crash
        print(f"❌ An error occurred during backup: {e}")
        return False

def list_available_backups(limit=5):
    """
    Lists the most recent .sql backup files from Google Drive.
    """
    try:
        service = authenticate_google_drive()
        if not service:
            return []

        # Query: Find files with 'backup_' in name, ending in .sql, not trashed
        query = "name contains 'backup_' and name contains '.sql' and trashed = false"
        
        results = service.files().list(
            q=query,                                    # The search query string
            pageSize=limit,                             # Limit the number of results returned (e.g., show only 5)
            orderBy="createdTime desc",                 # Order results by creation date, descending (Newest first)
            fields="files(id, name, createdTime)"       # Request only these specific fields back for efficiency
        ).execute()
        
        # Use .get() defensively to ensure it returns an empty list [] if 'files' key is missing
        items = results.get('files', [])
        return items
        
    except Exception as e:
        print(f"❌ Error fetching backup list: {e}")
        return []

def restore_backup(file_id):
    """
    Downloads a backup file and imports it into MySQL (Overwriting current data).
    """
    try:
        service = authenticate_google_drive()
        if not service:
            return False
        
        # Create the request to download the file content (get_media)
        request = service.files().get_media(fileId=file_id)
        
        # Create an in-memory buffer to hold the downloaded data temporarily
        fh = io.BytesIO()
        
        # Create the downloader object, setting the in-memory buffer (fh) as the destination
        downloader = MediaIoBaseDownload(fh, request)
        
        print("⏳ Downloading backup file...")
        done = False
        while done is False:
            # Download the file chunk by chunk (loop until download is finished)
            status, done = downloader.next_chunk()
        
        # Open the local database file in 'write binary' mode ('wb')
        # Save to a temporary local file
        temp_sql_file = "restore_temp.sql"
        with open(temp_sql_file, 'wb') as f:
            fh.seek(0)           # Move cursor to the beginning of the downloaded data in the buffer
            f.write(fh.read())   # Write the entire downloaded content, replacing all current data in the file

        print("⏳ Importing data into MySQL...")
        
        # Step 2: Run 'mysql' command to import data
        # We open the file in read mode ('r') to feed it into mysql command
        with open(temp_sql_file, 'r') as f:
            args = [MYSQL_CMD_PATH, '-u', DB_USER, f'-h{DB_HOST}', DB_NAME]
            if DB_PASSWORD:
                args.append(f'-p{DB_PASSWORD}')

            # stdin=f means "take input from this file"
            process = subprocess.Popen(args, stdin=f)
            process.wait()
            
        if process.returncode != 0:
            print("❌ Error: MySQL import failed.")
            return False
            
        # Step 3: Cleanup
        if os.path.exists(temp_sql_file):
            os.remove(temp_sql_file)
            
        print("✅ Restore Completed Successfully!")
        return True    

    except Exception as e:
        # Catch errors like network failure during download or disk access issues
        print(f"❌ Restore failed: {e}")
        return False

# ==========================================
# 4. GUI HELPER FUNCTIONS
# ==========================================

def gui_get_backup_list():
    """
    GUI Helper 1: Fetches the list and returns formatted strings for display.
    Updates the global 'cached_backups_list'.
    Returns: List of strings e.g. ["1. backup_name (date)", ...]
    """
    global cached_backups_list
    
    raw_files = list_available_backups(limit=5)
    cached_backups_list = raw_files  # Cache data for later use
    
    display_list = []
    if not raw_files:
        return ["No backups found."]
        
    for i, file in enumerate(raw_files):
        # Format: Index. Name (Created Time)
        created_time = file.get('createdTime', 'Unknown Date')
        display_str = f"{i+1}. {file['name']} ({created_time})"
        display_list.append(display_str)
        
    return display_list

def gui_restore_by_index(index):
    """
    GUI Helper 2: Restores a backup based on the list index (1, 2, 3...).
    Input: index (int or str) - The number selected by the user.
    Returns: (bool, message)
    """
    global cached_backups_list
    
    try:
        idx = int(index)
        
        if 0 <= idx < len(cached_backups_list):
            target = cached_backups_list[idx]
            print(f"GUI: Restoring {target['name']}...")
            
            success = restore_backup(target['id'])
            
            if success:
                return True, f"✅ Successfully restored: {target['name']}"
            else:
                return False, "❌ Restore failed. Check console."
        else:
            return False, "❌ Invalid selection."
            
    except Exception as e:
        return False, f"Error: {e}"

def gui_create_backup():
    """
    GUI Helper 3: Triggers a new backup.
    Returns: (bool, message)
    """
    print("GUI: Starting backup...")
    success = create_backup()
    if success:
        return True, "✅ Backup created successfully!"
    else:
        return False, "❌ Backup failed."
