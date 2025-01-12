import smtplib
from logger import log
import asyncio

# async def Connect():
#     sender_email = "kforkaranveer@gmail.com"
#     password = "znci xbiy akmi ipsf"
#     to_email = "kforkaranveer@gmail.com"
    
#     return sender_email, password, to_email
    
# def Send_email(name, value):
async def Send_email(name, value, previous_value):
    sender_email = "kforkaranveer@gmail.com"
    password = "znci xbiy akmi ipsf"    
    to_email = "kforkaranveer@gmail.com"
    # try:
    #     sender_email, password, to_email = await Connect()
    #     log.info("Connecting to SMTP")
    # except Exception as e:
    #     log.info("Couldn't connect to SMTP!")
    
    
    subject = f"{name.upper()} Value exceeded limit: {value}"
    edited_body = f"""
    <html>
        <body>
            <p style="font-size: 16px; color: #333;">
                <strong>{name.upper()}</strong> Value exceeded 1500!
            </p>
            <p style="font-size: 16px; color: #555;">
                Current Value: <strong>{value}</strong>
            </p>
            <p style="font-size: 16px; color: #555;">
                Previous Value: <strong>{previous_value}</strong>
            </p>
            <p style="font-size: 14px; color: #888; margin-top: 20px;">
                - LCA Notify
            </p>
        </body>
    </html>
    """
    message = f"Subject: {subject}\nContent-Type: text/html\n\n{edited_body}"


    
    server = "smtp.gmail.com"
    port = 587
    try:
        with smtplib.SMTP(server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, message)
        log.info("Connected to SMTP!")
    except Exception as e:
        log.error(f"Couldnt send notification: {e}")
        
