from guide_match.wsgi import *
from django.utils.text import slugify
from users.models import Guide
import csv
import re

f = open("BITRIX.csv")
csvreader = csv.reader(f)

for row in csvreader:
    guide = Guide()

    if row[10] not in ("Tokyo", "Osaka", "Kyoto"):
        continue
    
    guide.region = row[10]

    # name
    name_first = row[0].strip()
    name_last = row[1].strip()

    e = "^(Ms. )?[a-zA-Z\"]+(\,?[ -]{1}[a-zA-Z\"]+)*$"
    if re.match(e, name_first):
        guide.name_en = name_first
        if re.match(e, name_last):
            guide.name_en += f" {name_last}"
        else:
            guide.name_jp = name_last
    elif re.match(e, name_last):
        guide.name_en = name_last
        guide.name_jp = name_first
    else:
        continue

    guide.username = slugify(guide.name_en)
    guide.set_password("12345678")

    # phone
    phone = row[3] or row[4]
    guide.phone = phone

    guide.has_national_license = True
    
    if(guide.save(force_insert=True)):
        print(guide.username)
f.close()