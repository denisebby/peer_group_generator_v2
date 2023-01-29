import pymsteams
import pickle

if __name__=="__main__":
    webhook_url = os.environ["PEER_GROUP_WEBHOOK_URL"]
    msteams_notifications = pymsteams.connetorcard(webhook_url)
    # sky blue color
    msteams_notifications.color("#87CEEB")
    message = f""" 
        yeah
    """
    title = f"Some"
    msteams_notifications.text(message)
    msteams_notifications.title(title)
    # send the message
    msteams_notifications.send()
    