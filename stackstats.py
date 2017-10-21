#!/usr/bin/python
import datetime
import pytz
import time
import requests
import json
import argparse # used to parse arguments
import operator # used to sort scores dicionary

# This section is for argument things
parser = argparse.ArgumentParser(description="Simple python app to consume stackexchange API and calculate simple statistics.")
parser.add_argument("-s", "--since", type=str, required=True, help="Start date/time in YYYY-MM-DD HH:MM:SS format.")
parser.add_argument("-u", "--until", type=str, required=True, help="End date/time in YYYY-MM-DD HH:MM:SS format.")

args = parser.parse_args()

# Create naive datetime objects from raw_input
datetime1 = datetime.datetime.strptime(args.since, '%Y-%m-%d %H:%M:%S')
datetime2 = datetime.datetime.strptime(args.until, '%Y-%m-%d %H:%M:%S')

# Convert from naive to aware utc
localTimezone = pytz.timezone("Europe/Athens")
local_dt1 = localTimezone.localize(datetime1, is_dst=None)
local_dt2 = localTimezone.localize(datetime2, is_dst=None)
utc_dt1 = local_dt1.astimezone (pytz.utc)
utc_dt2 = local_dt2.astimezone (pytz.utc)

# Convert to epoch timestamp
epoch1 = int(time.mktime(utc_dt1.timetuple()))
epoch2 = int(time.mktime(utc_dt2.timetuple()))

# Attempt API call (with user definde date/time range)
url = 'https://api.stackexchange.com/2.2/answers?fromdate='+str(epoch1)+'&todate='+str(epoch2)+'&order=asc&sort=activity&site=stackoverflow'
response = requests.get(url)
response = response.json()

total = 0 # counter to track the total number of answers received
ids='' # string var to add all answer_ids to and use it to make comments API call
totalAcceptedAnswers = 0
totalScoreOfAcceptedAnswers = 0
scores = {} # dictionary that contains scores for each answer
questionIDs = [] # this list contains the unique question_ids that we get
for item in response['items']:
    ids = ids + str(item['answer_id']) + ';'
    total += 1
    if item['is_accepted']:
        totalAcceptedAnswers += 1
        totalScoreOfAcceptedAnswers += item['score']
        question = str(item['question_id'])
        answer = item['answer_id']
        score = item['score']
        if not(question in questionIDs):
            questionIDs.append(question)
        scores[answer] = score

ids = ids[:-1] #Remove last semicolon from ids so that the api recognizes all ids

# ==================== COMMENTS SECTION =====================================
commentsUrl = 'https://api.stackexchange.com/2.2/answers/'+ids+'/comments?order=desc&sort=creation&site=stackoverflow'
response = requests.get(commentsUrl)
response = response.json()
comments = [] # this list contains all post_ids for comments
for item in response['items']:
    answer = item['post_id']
    comments.append(answer)


# ===================== STATS SECTION =====================================
# the total number of accepted answers.
print "==================================|===="
print "total_accepted_answers            |" + str(totalAcceptedAnswers)

# the average score for all the accepted answers.
average = float(totalScoreOfAcceptedAnswers)/float(totalAcceptedAnswers)
print "accepted_answers_average_score    |" + str(average)

# the average answer count per question
average = float(totalAcceptedAnswers/len(questionIDs))
print "average_answers_per_question      |" + str(average)
print "==================================|===="

# the comment count for each of the 10 answers with the highest score.
print "   top_ten_answers_comment_count  |"
print "==================================|===="
sortedScores = sorted(scores.items(), key=operator.itemgetter(1), reverse = True) # sorted by score list of tuples (answer, score)
if len(sortedScores) < 10: # if we have less than 10 answers, take all the answer_ids
    first10Answers = [int(i[0]) for i in sortedScores]
else: # if we have >= 10 answers, get the first 10 answer_ids (highest scores)
    first10Answers = []
    flag = 0
    for i in sortedScores:
        if flag < 9:
            first10Answers.append(i[0])
            flag +=1

commentCount = {} # dictionary that contains first 10 answers with their comment count
for answer in first10Answers:
    count = comments.count(answer)
    commentCount[answer] = count

for k in commentCount:
    print "              "+str(k) + "            | " + str(commentCount[k])
print "==================================|===="
