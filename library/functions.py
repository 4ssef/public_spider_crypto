import imaplib
import email
import os
import mimetypes
import linecache
import requests
import pandas
import json
import datetime as dt
from bs4 import BeautifulSoup
from re import findall

# outlook credentials
username = "youremailaddress@whatever.com"
password = "yourPassword"

mail = imaplib.IMAP4_SSL("imap-mail.outlook.com") # connects to protocol
mail.login(username, password) # logs in with credentials
mail.select("Inbox/yourSubfolderName") # goes to selected subfolder
result, data = mail.uid('search', None, "ALL") # returns each email id
emailList = data[0].split() # list of emails that are found in yourSubfoldername

# saves emails in .html files for each transaction
def saveEmails(path_to_save: str):
	# if path_to_save doesn't exist, creates it
	if not os.path.exists(path_to_save):
		os.makedirs(path_to_save)
	
	# truncates folder which contains all emails (.html files)
	for f in os.listdir(path_to_save):
		os.remove(os.path.join(path_to_save, f))
	
	# saves emails
	i = 1
	for item in emailList:
		result2, data2 = mail.uid('fetch', item, '(RFC822)')
		raw_email = data2[0][1].decode("utf-8") # decodes email to string
		emailMessage = email.message_from_string(raw_email) # turns string to email object
		emailSubject = clean_email_subject(emailMessage['Subject']) # email subject
		
		for part in emailMessage.walk():
			if part.get_content_maintype() == "multipart":
				continue
			filename = part.get_filename()
			content_type = part.get_content_type()
			if not filename:
				extension = mimetypes.guess_extension(content_type)
				if not extension:
					extension = '.bin'
				filename = 'trsc_%00d__%s%s' %(i, emailSubject, extension) # .html files naming format
				# trsc_1__yyyy-MM-dd_hh,mm,ss.hmtl
			i += 1
		
		# saves emails in given path
		with open(os.path.join(path_to_save, filename), 'wb') as fp:
			fp.write(part.get_payload(decode = True))

# returns crypto price at given date/time
def get_crypto_price(symbol_of_crypto: str, date_of_transaction):
	# date_of_transaction parameter must contain yyyy MM dd hh mm (not ss)
	# binance api documentation: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#klinecandlestick-data
	url = 'https://api.binance.com/api/v3/klines' # url API
	date = date_of_transaction.timestamp() * 1000 # date on POSIX format (epoch)

	symbol = symbol_of_crypto.upper() + "USDT" # cryptocurrency symbol on Binance
	interval = '1m' # transaction's granularity (see documentation)
	startTime = str(int(date)) # start date
	endTime = str(int(date + 1)) # end date (start date + 1 nanosecond) (basically price of startTime)
	limit = '100' # rows max number

	parameters = {
		"symbol": symbol,
		"interval": interval,
		"startTime": startTime,
		"endTime": endTime,
		"limit": limit
	}

	database = pandas.DataFrame(json.loads(requests.get(url, params = parameters).text)) # creates price DB
	database = database.iloc[:, 0:5] # choose first 5 columns
	database.columns = ['datetime', 'open', 'high', 'low', 'close'] # names columns
	database.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in database.datetime] # converts epoch to human date
	
	# if there isn't any data, returns None
	if len(database.index) == 0:
		return None

	return database.iloc[0]['close'] # returns ONLY price at given date/time

# writes each transaction in .csv file
def createDB(path_of_folder: str, number_of_files: int, file_to_edit: str):
	list_of_files = os.listdir(path_of_folder) # list of files in given folder
	
	# writes content in .csv file (id, date, quantityBTC, priceBTC)
	def write_content_on_file(file_to_edit):
		idTransaction = str(i + 1)
		year = int(left(right(list_of_files[i], 24), 4)) # yyyy
		month = int(left(right(list_of_files[i], 19), 2)) # MM
		day = int(left(right(list_of_files[i], 16), 2)) # dd
		hour = int(left(right(list_of_files[i], 13), 2)) # hh
		minute = int(left(right(list_of_files[i], 10), 2)) # mm
		second = int(left(right(list_of_files[i], 7), 2)) # ss
		transactionDate = dt.datetime(year, month, day, hour, minute, second) # transaction date (UTC)
		price = get_crypto_price("CRYPTOSYMBOL", dt.datetime(year, month, day, hour, minute)) # chosen crypto price at transaction date
		
		file_to_edit.write(idTransaction + ";" + str(transactionDate) + ";" + 
				cryptoQty[0] + ";" + price + "\n")
	
	# writes and repeats for n number of files in path_of_folder
	for i in range(0, number_of_files):
		filePath = path_of_folder + "/" + list_of_files[i] # each email file path
		line = find_str_in_file(filePath, "received") # returns line number which matched with given string ("received")
		lineText = linecache.getline(filePath, line) # returns text of given line
		
		cryptoQty = findall("\d+\.\d+", lineText) # returns float of given line (crypto quantity)
		write_content_on_file(file_to_edit) # writes on file
			
	file_to_edit.close()

# cleans email subject of invalid characters in order to name files in Windows
def clean_email_subject(subject_of_email: str):
	shortEmail = right(subject_of_email, 24)
	shortEmail = left(shortEmail, 19) # removes "UTC" out of subject
	cleanEmail = shortEmail.replace(":", ",")
	return cleanEmail.replace(" ", "_")

# returns number of files at given path
def check_number_of_files(path_to_check: str):
	return len(os.listdir(path_to_check))

# finds string in given file and returns first match line
def find_str_in_file(path_to_file_to_find: str, string_to_find: str):
	line_number = 0
	list_of_results = []
	with open(path_to_file_to_find, 'r') as read_obj:
		for line in read_obj:
			line_number += 1
			if string_to_find in line:
				return line_number

# writes headers in .csv file
def writeHeader(file):
	file.write("idTransaction;dateTransaction(UTC);qtyCrypto;priceCrypto" + "\n")

# returns last n characters (right to left)
def right(string: str, n):
	return string[-n:]

# returns first n characters (left to right)
def left(string: str, n):
	return string[:n]

# manually writes transactions in .csv file using (symbol, qty and transaction date)
def create_transactions_DB(symbol_of_crypto, crypto_qty, date, file_to_edit: str):
	file_to_edit.write(symbol_of_crypto.upper() + ";" + str(crypto_qty) + ";" + str(date) + ";" + 
				get_crypto_price(symbol_of_crypto, date) + "\n")
	file_to_edit.close()