import re
import long_responses as long
import db as db_fxn
# import Response
import util
from decision_tree_processing import *

ageAsking = False

def message_probability(user_message, recognised_words, single_response=False, required_words=[]):
    message_certainty = 0
    has_required_words = True

    # Counts how many words are present in each predefined message
    # Counts how many words from the user are in the predefined message
    for word in user_message:
        if word in recognised_words:
            message_certainty += 1

    # Calculates the percent of recognised words in a user message
    percentage = float(message_certainty) / float(len(recognised_words))

    # Checks that the required words are in the string
    for word in required_words:
        if word not in user_message:
            has_required_words = False
            break

    # Must either have the required words, or be a single response
    if has_required_words or single_response:
        return int(percentage * 100)
    else:
        return 0

def extractSymptomsFromMessage(message):
    for i in message:
        if (i in db_fxn.SYMPTOMS):
            symptomsArray.add(i)

def check_all_messages(message):
    highest_prob_list = {}

    # Simplifies response creation / adds it to the dict
    def response(bot_response, list_of_words, single_response=False, required_words=[]):
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = message_probability(message, list_of_words, single_response, required_words)

    # iterate over dictionary of responses
    for key in responses:
        response(key, responses[key].list_of_words, responses[key].single_response, responses[key].required_words)

    # Longer responses
    response(long.R_ADVICE, ['give', 'advice'], required_words=['advice'])
    response(long.R_EATING, ['what', 'you', 'eat'], required_words=['you', 'eat'])

    # calculate which has the highest probability to users input
    best_match = max(highest_prob_list, key=highest_prob_list.get)
    # here we check if we need extract the symptoms for later use in the query
    if(responses[best_match].db and age == 0):
        extractSymptomsFromMessage(message)
        global ageAsking
        ageAsking = True

    # print(highest_prob_list)
    # print(f'Best match = {best_match} | Score: {highest_prob_list[best_match]}')

    return long.unknown() if highest_prob_list[best_match] < 1 else best_match

def findDisorder(root):
    # root = DecisionTree
    # root = tree_xml.getroot()
    for child in root:
        # this means the disorder is already located
        if(child.tag == "Disorder"):
            print("Bot: => Your disorder is: " + child.get("name"))
            break
        print("Bot: Do you have this symptom: " + child.get("feature") + "?")
        answer = input("You: ")
        if(answer == child.get("answer")):
            # firstly check if this node had the 
            # start checking inside the nested node
            return findDisorder(child)          
        else:
            return findDisorder(root[1])
# Used to get the response
def get_response(user_input):
    if(age != 0):
        # create decision tree
        decision_tree = db_fxn.createDecisionTree(symptomsArray, int(age))
        tree_xml = decision_tree_to_xml(decision_tree[0], feature_names=decision_tree[2], class_names=decision_tree[0].classes_)
        tree_xml.write('decision_tree2.xml')
        print("Bot: We are going to ask you questions, answer with yes or no")
        # processing decision tree
        findDisorder(tree_xml.getroot())

        return "You can now exit!"
    else:
        split_message = re.split(r'\s+|[,;?!.-]\s*', user_input.lower())
        response = check_all_messages(split_message)
        return response

# chat is going to be a dictionary where they key is what "You" write and hthe value is going to be what "Bot" answers
chat = {}
symptomsArray = set()
responses = util.initializeResponses()
age = 0
# Testing the response system
while True:
    you = input('You: ')
    if(you == "exit"):
        print(chat)
        break
    
    if(ageAsking):
        if(you.isdigit()):
            if(int(you) >=4  and int(you)):
                age = you
                ageAsking = False
            else:
                print("Bot: Your age is inappropriate for this bot!")
                continue
        else:
            print("Bot: Please write your age correctly!")
            continue
    bot = get_response(you)
    chat[you] = bot
    print("Bot: " + bot)