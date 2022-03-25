import os
CRICDATA_API_KEY = os.environ.get('CRICDATA_API_KEY')

if not CRICDATA_API_KEY:
    raise Exception('CRICDATA_API_KEY not set in env')
