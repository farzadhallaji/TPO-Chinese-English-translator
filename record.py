import sys
import sqlite3
import numpy as np

if len(sys.argv)!= 2:
    print("Usage: python script.py <string>")
    sys.exit(1)

user_input = sys.argv[1]
#print("You entered:", user_input)
search_string = 'TPO_0' + user_input

##################################### Reading #####################################################
R_types = ['Factual Information Questions事实信息题', 'Fill in a Table Question表格题', 'Inference Questions推理题', 'Insert Text Questions句子插入题', 'Negative Factual Information Questions否定事实信息题', 'Organization Questions组织结构题', 'Prose Summary Questions概要小结题', 'Reference Questions指代题', 'Rhetorical Purpose Questions修辞目的题', 'Sentence Simplification Questions句子简化题', 'Vocabulary Questions词汇题  ']

conn = sqlite3.connect('./store/TPOV4.0.8_Win64/Resources/toefltporead.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT reading_question_questionId, reading_question_articleQuestion_RightAnswer, reading_question_articleQuestion_CategoryName, reading_question_articleOrder
    FROM tpo_reading_question
    WHERE reading_question_questionId LIKE?
    ORDER BY reading_question_questionId ASC
""", (search_string + '%',))
rightAnswers = {}
Rqtypes = {}
Rqp = [] 
results = cursor.fetchall()
for row in results:
    rightAnswers[row[0]] = row[1]
    Rqtypes[row[0]] = row[2]
    Rqp.append(row[3])
conn.close()
#print(rightAnswers)
conn = sqlite3.connect('tpouser.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT questionId, answerTime, userChoice
    FROM readAnswer
    WHERE questionId LIKE?
""", (search_string + '%',))
results = cursor.fetchall()
userAnswers = {qid:set() for qid in rightAnswers.keys()}
userRTypes_error = [0 for R_type in R_types]
userAnswerTimes = {qid:0 for qid in rightAnswers.keys()}
for row in results:
    userAnswers[row[0]] = row[2]
    userAnswerTimes[row[0]] = int(row[1])//1000
conn.close()
#print(userAnswers)
#print(userAnswerTimes)
_, Rqpcount = np.unique(Rqp, return_counts=True)
reading_corrects = []
reading_times = []
for i, (qid, yranswer) in enumerate(rightAnswers.items()):
    if '-' in yranswer:
        CAns = yranswer.split('-')
        UAns = userAnswers[qid].split('-')
        op1 = set(CAns[0]) - set(UAns[0])
        op2 = set(CAns[1]) - set(UAns[1])
        k = len(CAns[0])+len(CAns[1])
        crt = (k-len(op1)+len(op2))/k* 3
        if crt < 3 and userAnswerTimes[qid]>0:
            userRTypes_error[R_types.index(Rqtypes[qid])] += 1
            
        #reading_corrects.append(0)
        #reading_times.append(0)
        
    elif len(yranswer) == 3:
        ranswer = set(yranswer)
        userAnswers[qid] = set(userAnswers[qid])
        crt = ((len(ranswer) - len(ranswer-userAnswers[qid]))/len(ranswer)) * 2
        if crt < 2 and userAnswerTimes[qid]>0:
            userRTypes_error[R_types.index(Rqtypes[qid])] += 1
    else:
        ranswer = set(yranswer)
        userAnswers[qid] = set(userAnswers[qid])
        crt = ((len(ranswer) - len(ranswer-userAnswers[qid]))/len(ranswer))
        if crt < 1 and userAnswerTimes[qid]>0:
            userRTypes_error[R_types.index(Rqtypes[qid])] += 1
        
    crt = round(crt, 2)
    if crt == 1:
        crt=1
    elif crt==0:
        crt=0
    #if crt ==3:
        #print(qid)
    reading_corrects.append(crt)
    reading_times.append(userAnswerTimes[qid])
    

print(f'TPO {user_input} Reading ...')
qsum = 0
for rqpc in Rqpcount:
    print(','.join(map(str, reading_corrects[qsum:qsum+rqpc])))
    print(','.join(map(str, reading_times[qsum:qsum+rqpc])))
    qsum+=rqpc
print()
print(','.join(map(str, userRTypes_error)))

print('\n','#'*80,'\n')
##################################### Listening #####################################################

L_types = ['Connecting Content Questions信息连结题','Detail Questions细节题','Gist-content Questions 内容主旨题','Gist-purpose Questions 目的主旨题','Making Inference Questions推理题','Understanding Organization Questions 组织结构题','Understanding the Function of What Is Said Questions 功能题','Understanding the Speaker’s Attitude Questions 态度题']
conn = sqlite3.connect('./store/TPOV4.0.8_Win64/Resources/toefltpolisten.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT listening_question_questionId, listening_question_questionRightAnswer, listening_question_questionCategoryName
    FROM tpo_listening_question
    WHERE listening_question_questionId LIKE?
    ORDER BY listening_question_questionId ASC
""", (search_string + '%',))
rightAnswers = {}
Lqtypes = {}
results = cursor.fetchall()
for row in results:
    rightAnswers[row[0]] = set(row[1])
    Lqtypes[row[0]] = row[2]
conn.close()
#print(rightAnswers)
assert len(rightAnswers) == 34
conn = sqlite3.connect('tpouser.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT listening_questionId, answerTime, userChoice
    FROM listenAnswer
    WHERE listening_questionId LIKE?
""", (search_string + '%',))
results = cursor.fetchall()
userAnswers = {qid:set() for qid in rightAnswers.keys()}
userLTypes_error = [0 for L_type in L_types]
userAnswerTimes = {qid:0 for qid in rightAnswers.keys()}
for row in results:
    userAnswers[row[0]] = set(row[2])
    userAnswerTimes[row[0]] = int(row[1])//1000
conn.close()
#print(userAnswers)
#print(userAnswerTimes)
listening_corrects = []
listening_times = []
for qid,ranswer in rightAnswers.items():
    crt = int((len(ranswer) - len(ranswer-userAnswers[qid]))/len(ranswer))
    if crt < 1 and userAnswerTimes[qid]>0:
        userLTypes_error[L_types.index(Lqtypes[qid])] += 1
    listening_corrects.append(crt)
    listening_times.append(userAnswerTimes[qid])

print(f'TPO {user_input} Listening ...')
print(','.join(map(str, listening_corrects[:17])))
print(','.join(map(str, listening_times[:17])))
print(','.join(map(str, listening_corrects[17:])))
print(','.join(map(str, listening_times[17:])))
print()
print(','.join(map(str, userLTypes_error)))
print()
#print(', '.join(map(str, listening_corrects[:5])))
#print(', '.join(map(str, listening_times[:5])))
#print(', '.join(map(str, listening_corrects[5:11])))
#print(', '.join(map(str, listening_times[5:11])))
#print(', '.join(map(str, listening_corrects[11:17])))
#print(', '.join(map(str, listening_times[11:17])))
#print(', '.join(map(str, listening_corrects[17:22])))
#print(', '.join(map(str, listening_times[17:22])))
#print(', '.join(map(str, listening_corrects[22:28])))
#print(', '.join(map(str, listening_times[22:28])))
#print(', '.join(map(str, listening_corrects[28:34])))
#print(', '.join(map(str, listening_times[28:34])))

##########################################################################################



