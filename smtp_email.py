import smtplib
from logger import log
import asyncio

async def Connect():
    sender_email = "kforkaranveer@gmail.com"
    password = "znci xbiy akmi ipsf"
    to_email = "kforkaranveer@gmail.com"
    
    return sender_email, password, to_email
    
async def Send_email(name, value):
    try:
        sender_email, password, to_email = await Connect()
        log.info("Connecting to SMTP")
    except Exception as e:
        log.info("Couldn't connect to SMTP!")
    
    log.info("Connected to SMTP!")
    
    subject = f"{name} Value exceeded! {value}"
    edited_body = f"""
    {name} Value exceeded 1500!
    Value = {value}
    """
    message = f"Subject: {subject}\n\n{edited_body}"
    
    server = "smtp.gmail.com"
    port = 587
    
    with smtplib.SMTP(server, port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, message)
        
