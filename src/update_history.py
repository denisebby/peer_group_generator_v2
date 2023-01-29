import pickle
import random
from datetime import date, datetime, timedelta
from typing import Tuple

from itertools import combinations
from collections import OrderedDict, defaultdict

import logging
import logging.handlers

import os
import yaml

########################################################################################
# Set up logging
########################################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    MY_SECRET = os.environ["MY_SECRET"]
except KeyError:
    MY_SECRET = "MY_SECRET not found!"

########################################################################################
# Helper functions to generate optimal groupings that 
# minimize the number of past interactions
########################################################################################
def get_pairs_so_far(history: dict, teams: dict) -> defaultdict:
    """
    Description:
        Based on history, get # of occurences of people meeting

    Args:
        history (dict of datetime.date : frozenset(frozenset)): 
            the history of past groups

        teams (dict of str: list[str]): 
            dictionary outlining prexisting teams. We include this to ensure people 
            initially are not matched with people they already see on a regular cadence


    Returns:
        pairs_so_far (defaultdict of frozenset: int):
            Default dictionary where keys are frozenset of a pair and value is 
            # of past interactions, default value of 0
    """
    
    pairs_so_far = defaultdict(int)
    
    # count occurences in history
    for time, val in history.items():
        for elem in list(val):
            for pair in combinations(elem, 2):
                pairs_so_far[frozenset(pair)] += 1
    
    # count occurences in teams
    for team_name, team in teams.items():
        for pair in combinations(team, 2):
            pairs_so_far[frozenset(pair)] += 1
                
        
    return pairs_so_far

def assign_score(candidate, pairs_so_far)->int:
    """
    Description:
        Assign score (the number of past interactions) for a candidate group

    Args:
        candidate (frozenset(frozenset)): a candidate grouping

        pairs_so_far (defaultdict of frozenset: int): 
            Default dictionary where keys are frozenset of a pair and value is 
            # of past interactions, default value of 0

    Returns:
        score (int): # number of past interactions for the entire grouping
        
    """
    score = 0
    for elem in list(candidate):
        for pair in combinations(elem, 2):
            score += pairs_so_far[frozenset(pair)] 
    return score

def choose_group_splits(num_people)->dict:
    """ 
    Description:
        Choose how many groups of 4 and how many groups of 3 to generate

    Args:
        num_people (int): the number of people we're grouping

    Returns:
        split_strategy (dict[str]=int): 
            a dictionary with key group size and value number of groups
    """
    if num_people%4 == 0:
        return {"four": num_people//4, "three": 0}
    elif num_people%3 == 0:
        return {"four": 0, "three": num_people//3}
    else:
        split_strategy = {"four": 0, "three": 0}
        while num_people %3  != 0:
            num_people -= 4
            split_strategy["four"] += 1
        
        while num_people != 0:
            num_people -= 3
            split_strategy["three"] += 1
        
        return split_strategy

def generate_random_groups(people, pairs_so_far, n=1000) -> Tuple[dict, defaultdict]:
    """
    Description:
        Generate n random samples of groupings and keep track of the score. 
        This function also outputs a default dictionary that keeps track of the 
        frequency of the groupings occuring in the random sample

    Args:
        people (list[str]): a list of people for which to generate groups 

        pairs_so_far (defaultdict of frozenset: int): 
            Default dictionary where keys are frozenset of a pair and value is 
            # of past interactions, default value of 0

        n=1000 (int): # of samples to generate, default is 1000

    Returns:

        sample_score_dict (dict of frozenset(frozenset): int): 
            dictionary of key grouping and value score i.e. # of past interactions 
            among people

        repeat_samples_dict (defaultdict of frozenset(frozenset): int): 
            default dictionary of frequency of that grouping among samples generated
    """

    num_people = len(people)
    split_strategy = choose_group_splits(num_people)
    
    sample_score_dict = dict()
    repeat_samples_dict = defaultdict(int)
    for _ in range(n):
        # generate random sample by getting random order
        candidate_order = random.sample(people, num_people)
        
        g4 = candidate_order[0:split_strategy["four"]*4] 
        
        g4_2d = []
        i= 0
        while i < len(g4):
            g4_2d.append(frozenset(g4[i: i+4]))
            i+=4
        if split_strategy["three"] != 0:
            # get remaining part of list
            g3 = candidate_order[split_strategy["four"]*4:] 
            g3_2d = []
            i = 0
            while i < len(g3):
                g3_2d.append(frozenset(g3[i: i+3]))
                i+=3
        
        candidate = frozenset(g4_2d + g3_2d)
        sample_score_dict[candidate] = assign_score(candidate, pairs_so_far)
        repeat_samples_dict[candidate] += 1

    return sample_score_dict, repeat_samples_dict

def choose_best_sampled_group(sample_score_dict):
    """
    Description:
        Given the sampled groups with their scores, 
        choose a group that has the minimum score, i.e. the 
        least number of past interactions

    Args:
        sample_score_dict (dict of frozenset(frozenset): int): 
            dictionary of key grouping and value score i.e. # of past interactions 
            among people
            
    Returns:
        k (frozenset(frozenset)): 
            the best scored grouping that minimizes the number of past interactions
    """
    min_score = min(sample_score_dict.values())
    for k, v in sample_score_dict.items():
        if v == min_score:
            return k

########################################################################################
# Read and write history of groupings as picked object
########################################################################################

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

    run_status = read_history("data/run_status.pickle")
    # flip run status, we do this to run only every other week
    # cron job syntax for every other week is complicated
    write_history(not run_status, "data/run_status.pickle")
    if run_status:
       
        with open("config.yaml") as f:
            config = yaml.safe_load(f)
        f.close()

        people = config["people"]
        teams = config["teams"]

        # input params
        # TODO: paramaterize this as people come and go and teams change
        # people = ["Bridget", "Bud", "Carly", "Cody", "Denis", "Eunice", "Jie", "Jonathan", 
        #             "Kelly", "Kirtiraj", "Kyle B.", "Kyle C.", "Mohar", "Piyush", "Stan"]
        # teams = {"Team 1": ["Denis", "Mohar", "Jie", "Cody"]}

        history = read_history()
        # save a backup in case something goes wrong
        write_history(history, "data/backup_history.pickle")

        print(f"History # entries before update: {len(history)}")


        pairs_so_far = get_pairs_so_far(history, teams)

        scores_dict, freq = generate_random_groups(
                                people = people, 
                                pairs_so_far = pairs_so_far,
                                n = 1000
                            )

        final_group = choose_best_sampled_group(sample_score_dict = scores_dict)

        history[date.today()] = final_group

        write_history(history, "data/history.pickle")
        print(f"History # entries after update: {len(history)}")
        print("\n")
        print(f"most recent group: {final_group}")

        # We don't really use this secret, just seeing how it works
        logger.info(f"SECRET:{MY_SECRET}")
        logger.info(f"New group!: {final_group}")
    else:
        logger.info(f"SECRET:{MY_SECRET}")
        logger.info(f"Skipped this week")




