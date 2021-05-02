#!/usr/bin/env python
# -*- coding: utf-8 -*-
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from vaccineAvailabilityNotifier import get_logger


def create_email_template(slot):
    try:
        html = """\
        <html>
          <body>
              Hi, <br/>
              Vaccine is available on <strong> {} </strong> in the following centers: 
               <br/><br/>
            <strong> Center Name: {} </strong> <br/>
            Location: {}, {}, {} <br/>
            From {} to {} <br/>
            Fee Type: {} <br/>
            Fee: {} rupees <br/>
            Available Capacity: {} doses available <br/>
            Vaccine: {} <br/>
            Slots Available: {} <br/> 
              <br/> 
          </body>
        </html>
        """.format(slot['date'], slot['name'], slot['block_name'], slot['state_name'],
                   int(slot['pincode']), slot['from'], slot['to'], slot['fee_type'],
                   slot['fee'], slot['available_capacity'], slot['vaccine'], slot['slots'])
    except Exception as e:
        get_logger().error("An error has occurred while drafting  the email {}".format(e))
    return html


def notifyMe(slot, EMAIL, APPLICATION_PASSWORD):
    html_message = create_email_template(slot)
    sender_email = EMAIL
    receiver_email = EMAIL
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Covid Vaccine Availability Notification"
        message["From"] = sender_email
        message["To"] = receiver_email
        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(html_message, "plain")
        part2 = MIMEText(html_message, "html")
        message.attach(part1)
        message.attach(part2)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, APPLICATION_PASSWORD)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
    except Exception as e:
        get_logger().error("An error has occurred while notifying the user {}".format(e))
