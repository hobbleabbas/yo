import requests
from datetime import datetime
import reportlab
from reportlab.pdfgen import canvas
import time
import json
import os
import stripe
from flask import Flask, jsonify, request
import smtplib, ssl
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from reportlab.graphics import renderPS
from reportlab.graphics import renderPM
from reportlab.graphics import renderSVG

stripe.api_key = 'sk_test_51I32fFBeAy0pVJVkmgL8al5tEIZuGErH0G7AIBwbvIXPDwCsGFfHL3zxDvfSP0K0NWZ7ziXEWeJX2oBQTSdpIph900J4YWDF9D'

chargeid = input('What is the Charge ID? \n')

charge_raw = stripe.Charge.retrieve(
  chargeid,
)

receipts = [0]

new_receipt_num = receipts[-1] + 1
receipts.append(new_receipt_num)

charge_string = json.dumps(charge_raw)
chargedata = json.loads(charge_string)

donee_raw = stripe.Customer.retrieve(chargedata['customer'])
donee_string = json.dumps(donee_raw)
donee = json.loads(donee_string)

print(charge_raw)

title = 'Receipt of Charitable Donation'
description1 = 'This is an official tax receipt issued by Kinship Canada.'
description2 = 'A non-profit agency located in Canada. Charity Registration Number: 855070728 RR'
website = 'https://kinshipcanada.com'
email = 'info@kinshipcanada.com'
address = '43 Matson Drive, Bolton, ON. L7E 0B1'
ayat = '“If you do deeds of charity openly, it is well; but if you bestow it upon the needy in secret, it will be even better for you, and it will atone for some of your bad deeds. And God is aware of all that you do.”'
receipt = 'Access your receipt here: ' + chargedata['receipt_url']

while True:
    thecountry = chargedata['billing_details']['address']['country']
    if thecountry.lower() == 'ca':
        print("You are eligible for a tax receipt! \n Generating...")
        eligbility = 'YES'
        country = 'Canada'
        break
    else:
        print("You are not eligible")
        eligbility = 'NO'
        exit()

user_details = {
    'username': str(donee['name']).upper(),
    'address': donee['address']['line1'],
    'city': str(donee['address']['city']).title(),
    'postal code': str(donee['address']['postal_code']).upper(),
    'state': str(donee['address']['state']).upper(),
    'eligible': eligbility,
    'useremail': donee['email'],
}

ts = chargedata['created']
date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

if chargedata['paid'] == True:
    donation_status = 'Complete'
else:
    donation_status = 'There is an issue'

payment_details = {
    'Payment_ID': chargedata['payment_intent'],
    'Transaction_Key': '56c20802771b3537c03fb568ccac8671',
    'Transaction_ID': chargedata['id'],
    'Donation_Status': donation_status,
    'Payment_Method': chargedata['payment_method_details']['card']['brand'],
    'Donation_Name': 'General Donations',
    'Donation_Amount': (chargedata['amount'])/100,
    'Donation_Issue_Date': date,
}

canvas.Canvas(im = Image('Light Logo.png', width = 20, height=10))
im.hAlign = 'CENTER'
pdf = canvas.Canvas('Your Kinship Canada Tax Receipt.pdf')
pdf.setTitle('Tax Receipt')

pdf.drawString(220, 800, title)
pdf.drawString(200, 780, address)
pdf.drawString(20, 740, description1)
pdf.drawString(20, 720, description2)
pdf.drawString(20, 700, 'We are availible for contact at the following:')
pdf.drawString(40, 680, 'Email: ' + email)
pdf.drawString(40, 660, 'Website: ' + website)
pdf.drawString(20, 640, receipt)

pdf.drawString(20, 600, 'Invoice to: ')
pdf.drawString(20, 580, user_details['username'])
pdf.drawString(20, 560, user_details['address'])
pdf.drawString(20, 540, user_details['city'])
pdf.drawString(20, 520, user_details['postal code'])
pdf.drawString(20, 500, country.title())

pdf.drawString(20, 440, 'Payment ID: ' + payment_details['Payment_ID'])
pdf.drawString(20, 420, 'Transaction Key: ' + payment_details['Transaction_Key'])
pdf.drawString(20, 400, 'Transaction ID: ' + payment_details['Transaction_ID'])
pdf.drawString(20, 380, 'Donation Status: ' + payment_details['Donation_Status'])
pdf.drawString(20, 360, 'Donation Name: ' + payment_details['Donation_Name'])
pdf.drawString(20, 340, 'Payment Method: ' + (payment_details['Payment_Method']).upper())
pdf.drawString(20, 320, 'Donation Amount: ' + str(payment_details['Donation_Amount']) + ' ' + (chargedata['currency']).upper())
pdf.drawString(20, 300, 'Issue Date: ' + payment_details['Donation_Issue_Date'])

pdf.save()

subject = "Your CRA-Eligible Kinship Canada Tax Receipt"
sender_email = "husseinshakeel003@gmail.com"
receiver_email = user_details['useremail']
password = 'bruh126412'

message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email

message.attach(MIMEText("plain"))

filename = "Your Kinship Canada Tax Receipt.pdf"

with open(filename, "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

encoders.encode_base64(part)

part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filename}",
)

htmlraw = """\
<html>
  <head></head>
  <body>
    <p>Thank you for your donation!<br>
       Bruh<br>
       Here is the <a href""{0}">link</a> you wanted.
    </p>
  </body>
</html>
"""

html = htmlraw.format(receipt)

part2 = MIMEText(html, 'html')

message.attach(part)
message.attach(part2)
text = message.as_string()

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)