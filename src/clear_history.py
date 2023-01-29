import pickle

def write_history(object_to_save, location):
    """ 
    Description:
        Write object as pickled object
    Args:
        object_to_save (any Python object): an object to save
        location (str): where to write data 
    Returns: None
    """
    with open(location, 'wb') as handle:
        pickle.dump(object_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()
    
if __name__=="__main__":
    write_history(dict(), "data/history.pickle")
    write_history(True, "data/run_status.pickle")
