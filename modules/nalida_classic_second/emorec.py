"Module for Emotion Recording"

def is_emorec_response(message):
    "determines if message is emorec response"
    return message["data"]["text"] == '신난다'
