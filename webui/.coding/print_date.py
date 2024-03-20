# filename: print_date.py
from datetime import datetime

now = datetime.now()
print("Today's date is:", now.strftime("%A, %B %d, %Y"))