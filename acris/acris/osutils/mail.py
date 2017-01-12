#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acrisel LTD
#    Copyright (C) 2008- Acrisel (acrisel.com) . All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

"""Send the contents of a directory as a MIME message."""

import os
import sys
import smtplib
# For guessing MIME type based on file name extension
import mimetypes

from argparse import ArgumentParser

from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

COMMASPACE = ', '

def attach(outer, path):
    # Guess the content type based on the file's extension.  Encoding
    # will be ignored, although we should check for simple things like
    # gzip'd or compressed files.
    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        with open(path) as fp:
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
    elif maintype == 'image':
        with open(path, 'rb') as fp:
            msg = MIMEImage(fp.read(), _subtype=subtype)
    elif maintype == 'audio':
        with open(path, 'rb') as fp:
            msg = MIMEAudio(fp.read(), _subtype=subtype)
    else:
        with open(path, 'rb') as fp:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
        # Encode the payload using Base64
        encoders.encode_base64(msg)
    # Set the filename parameter
    msg.add_header('Content-Disposition', 'attachment', filename=path)
    outer.attach(msg)


def send_mail(mailto, subject, body='', mailfrom=[], mailcc=[], attachments=[], output=''):
    
    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    if not subject:
        subject = 'Content of directory'
        
    outer['Subject'] = subject
    if mailcc:
      outer['Cc'] = COMMASPACE.join(mailcc)
      
    outer['To'] = COMMASPACE.join(mailto)
    
    if not mailfrom:
        mailfrom="{}@{}".format(os.environ['USER'], os.environ['HOSTNAME'])
    outer['From'] = mailfrom

    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
    if body:
        outer.attach(MIMEText(body))
        
    for attachment in attachments: 
        if not os.path.isfile(attachment):
            for filename in os.listdir(attachment):
                path = os.path.join(attachment, filename)
                if not os.path.isfile(path):
                    continue
                attach(outer, path)
        else:
            attach(outer, attachment)
        
    # Now send or store the message
    composed = outer.as_string()
    if output:
        with open(output, 'w') as fp:
            fp.write(composed)
    else:
        with smtplib.SMTP('localhost') as s:
            s.send_message(outer)


if __name__ == '__main__':
    parser = ArgumentParser(description="""\
Send the contents of a directory as a MIME message.
Unless the -o option is given, the email is sent by forwarding to your local
SMTP server, which then does the normal delivery process.  Your local machine
must be running an SMTP server.
""")
    parser.add_argument('-a', '--attach', required=False, 
                        action='append', metavar='ATTACHMENT', default=[], dest='attachments',
                        help="""Mail the contents of the specified directory or file, Only the regular
                        files in the directory are sent, and we don't recurse to
                        subdirectories.""")
    parser.add_argument('-o', '--output', metavar='FILE',
                        help="""Print the composed message to FILE instead of
                        sending the message to the SMTP server.""")
    parser.add_argument('-s', '--subject', metavar='SUBJECT', required=True, 
                        help="""Subject for email message (required).""")
    parser.add_argument('-b', '--body', metavar='BODY', required=False,
                        help="""Boby text for the message (optional).""")
    parser.add_argument('-f', '--mailfrom', required=False,
                        help='The value of the From: header (optional); if not provided $USER@$HOSTNAME will be use as sender')
    parser.add_argument('-c', '--malicc', required=False,
                        help='The value of the CC: header (optional)', action='append', metavar='CC', 
                        default=[], dest='mailcc')
    parser.add_argument('-t', '--mailto', required=True, 
                        action='append', metavar='RECIPIENT',
                        default=[], dest='mailto',
                        help='A To: header value (at least one required)')
    args = parser.parse_args()
    send_mail(subject=args.subject, body=args.body, mailto=args.mailto, mailcc=args.mailcc, attachments=args.attachments, output=args.output)
