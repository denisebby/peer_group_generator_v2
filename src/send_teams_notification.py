import pymsteams
import pickle

import os
from dateutil.relativedelta import relativedelta, FR

def convert_from_fz_to_str(g):
    """ 
    Description: convert from frozenset(frozenset) to readable string
    """
    res = ""
    for elem in list(g):
        res += ",".join(list(elem))
        res += "; "
    return res

def read_history(location)->dict:
    """
    Description:
        Read object from pickled object
    Args:
        location (str): where to read data 
    Returns: 
        saved_object (any Python object): an object to save
    """
    with open(location, 'rb') as handle:
        saved_object = pickle.load(handle)
    handle.close()
    return saved_object

if __name__=="__main__":
    history = read_history("../data/history.pickle")

    most_recent_date = sorted(history.keys())[-1]
    most_recent_group = history[most_recent_date]
    
    newlist = [most_recent_date, most_recent_date + relativedelta(weekday=FR(+2))]
    
    readable_group = convert_from_fz_to_str(most_recent_group)
    date = " to ".join([str(x) for x in newlist])

    webhook_url = os.environ["PEER_GROUP_WEBHOOK_URL"]
    msteams_notifications = pymsteams.connetorcard(webhook_url)
    # sky blue color
    msteams_notifications.color("#87CEEB")
    title = f"Peer Groups for {date}!:"
    message = f"""{readable_group}"""
    msteams_notifications.text(message)
    msteams_notifications.title(title)
    # send the message
    msteams_notifications.send()
    