import requests

def Send_wapp(name, limit, value, body):
    
    message = f"""
    {name} Exceeded {limit},
    Current Value: {value}
    {body}
    """
    RECIEVER = 9915323456
    URL = f"http://148.251.129.118/wapp/api/send?apikey=3d27aec1ecef4ef2b3c4d13fe5112c3a&mobile={RECIEVER}&msg={message}"

    requests.post(URL)
    print(URL)
    