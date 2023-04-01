import csv
import phonenumbers

phone = phonenumbers.parse("", "RU")
phone1 = phonenumbers.parse("79233129860", "RU")
if phone == phone1:
    print("eq")
print(phone)