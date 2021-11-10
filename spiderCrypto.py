from shutil import copyfile
from library.functions import *

projectPath = "C:/Users/youruser/path/to/spiderCrypto"
emailsPath = projectPath + "/emails"
btc = open(projectPath + "/btc.csv", 'a') # opens local .csv file on append mode
btcDrive = "G:/path/to/csvfile/in/cloudStorageApp/btcDrive.csv" # (Google Drive, Microsoft OneDrive, Dropbox, etc.)

saveEmails(emailsPath) # saves emails at moment of execution

btc.truncate(0) # truncates content of local .csv file
writeHeader(btc) # writes header of columns on local .csv file
createDB(emailsPath, check_number_of_files(emailsPath), btc) # writes rows on local .csv file

copyfile(projectPath + "/btc.csv", btcDrive) # copies local .csv file to cloud storage app chosen