import os
from datetime import datetime

def get_latest_modified_file_date(directory):
    # Get the list of all files and directories in the specified directory
    all_entries = os.listdir(directory)
    
    # Initialize variable to track the latest date
    latest_date = None
    
    for entry in all_entries:
        # Create full path to the item
        full_path = os.path.join(directory, entry)
        
        # Check if it's a file
        if os.path.isfile(full_path):
            # Get the last modified date of the file
            modified_date = os.path.getmtime(full_path)
            
            # Update the latest_date if this file is newer
            if latest_date is None or modified_date > latest_date:
                latest_date = modified_date
    
    # Convert the latest modification timestamp to a readable format
    if latest_date is not None:
        return datetime.fromtimestamp(latest_date)
    else:
        return None
    

def should_reindex(docs, store):
    if not os.listdir(store):
        return True
    return get_latest_modified_file_date(docs) < get_latest_modified_file_date(store)