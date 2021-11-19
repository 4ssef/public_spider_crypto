# manually writes rows
from shutil import copyfile
from library.functions import create_transactions_DB
from time import sleep
import datetime as dt

projectPath = "C:/Users/youruser/path/to/spiderCrypto"
transactions = open(projectPath + "/transactions.csv", 'a') # opens local .csv file on append mode
transactionsDrivePath = "G:/path/to/csvfile/in/cloudStorageApp/transactionsDrive.csv" # (Google Drive, Microsoft OneDrive, Dropbox, etc.)

symbol = input("Crypto Symbol: ") # reads crypto symbol
trade = input("Trade Type (buy || sell): ") # reads type of trade
qty = float(input("Crypto Qty: ")) # reads crypto quantity

print("Transaction Date: ", end = '') # reads transaction date
year = int(input("yyyy: ")[:4])
month = int(input("MM: ")[:2])
day = int(input("dd: ")[:2])
hour = int(input("HH: ")[:2])
minute = int(input("mm: ")[:2])

transactionDate = dt.datetime(year, month, day, hour, minute) # transaction date

create_transactions_DB(symbol, qty, transactionDate, transactions) # creates .csv local file
copyfile(projectPath + "/transactions.csv", transactionsDrivePath) # copies local .csv file to cloud storage app chosen

# process completed
print("Process Completed!\n")
for i in range(3):
	print("Closing in " + str(i))
	sleep(1)