import requests

def Send_wapp(name, limit, value, body):
    
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
    RECIEVER = 9915323456
    URL = f"http://148.251.129.118/wapp/api/send?apikey=3d27aec1ecef4ef2b3c4d13fe5112c3a&mobile={RECIEVER}&msg={message}"

    requests.post(URL)
    print(URL)
    