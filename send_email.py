from email.mime.text import MIMEText
import smtplib
import random
from pathlib import Path
import glob
import boto3
from botocore.exceptions import ClientError
import os 
from dotenv import load_dotenv

def get_quote(feel):
    feel = feel.lower()
    availabel_feelings = glob.glob("quotes/*txt")
    availabel_feelings = [Path(filename).stem for filename in 
                            availabel_feelings]
    if feel in availabel_feelings:
        with open(f"quotes/{feel}.txt") as file:
            quotes = file.readlines()
        return random.choice(quotes)
    else:
        return "Please try another feeling"

def amazon_send_email(email, feeling, happiness_count, anger_count, sadness_count, motivation_count):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Sender Name <sender@example.com>"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = email

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    quote_to_send = get_quote(feeling)

    # The subject line for the email.
    SUBJECT = "Quote For You!"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Hey there! Your feeling is %s.\n" %feeling + 
        "Here is the quote based on your feeling:%s\n" %quote_to_send +
        "There are %s people with happiness" %happiness_count +
            "%s people with anger;" %anger_count +
            "%s people with sadness;" %sadness_count +
            "%s people with motivation." %motivation_count)
                
    # The HTML body of the email.
    BODY_HTML = "Hey there! Your feeling is <strong>%s</strong>.<br> \
        Here is the quote based on your feeling:<br><strong>%s</strong><br> \
        There are <strong>%s</strong> people with happiness; \
            <strong>%s</strong> people with anger; \
            <strong>%s</strong> people with sadness; \
            <strong>%s</strong> people with motivation." \
                %(feeling, quote_to_send, happiness_count, anger_count, sadness_count, motivation_count)     

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION, \
                            aws_access_key_id=os.environ['ACCESS_KEY'], \
                            aws_secret_access_key=os.environ['SECRET_KEY'])

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
