import csv

# This script analyzes the Mechanical Turk batch data from Amazon.
# Currently, it computes the RMSE on all questions answered at least twice.

# Set parameters.
num_questions = 9
human_verification_question_id = 6
# BATCH_NUMBER = '1915620'
BATCH_NUMBER = '1910583'
# BATCH_NUMBER = '1905281'
# BATCH_NUMBER = '1907174'
batch_csv_file = 'Batch_' + str(BATCH_NUMBER) + '_batch_results.csv'
human_answers_outfile = 'Batch_' + str(BATCH_NUMBER) + '_human_results.csv'
turk_answers_outfile = 'Batch_' + str(BATCH_NUMBER) + '_turk_results.csv'

INPUT_HUMAN_ANSWERS = False
USE_FIRST_TWO_ANSWERS_ONLY = True
WRITE_OUTPUT_CSV = True

# Load the raw batch data.
raw_batch_data = []
with open(batch_csv_file) as csvfile:
    csvreader = csv.reader(csvfile)
    headers = {}
    for index, header in enumerate(csvreader.next()):
        headers[header] = index
    for row in csvreader:
        raw_batch_data.append(row)

print('Num responses: %d' % len(raw_batch_data))

# Reformat the batch data as a dict. Keys are HITId's. Values are dicts of the form
#   {'questions': ['Q1...', ... , 'Qn'],
#    'answers': [
#                 [A11, A12, ...],
#                 ...
#                 [An1, An2, ...]
#               ]
#   },
# where n is the number of question for the given HIT, and Aij is the j-th Turk's answer to question i.
batch_data = {}
for batch in raw_batch_data:
    hit_id = batch[headers['HITId']]
    if hit_id not in batch_data:
        batch_data[hit_id] = {}
        questions = []
        for question_id in xrange(1, num_questions + 1):
            questions.append(batch[headers['Input.Quotation_HTML_' + str(question_id)]])
        batch_data[hit_id]['questions'] = questions
        batch_data[hit_id]['answers'] = [[] for _ in xrange(len(questions))]
    answers = []
    for answer_id in xrange(1, num_questions + 1):
        answer_index = answer_id
        if answer_id >= human_verification_question_id:
            answer_index += 1
        # Subtract one from answer_id in order to make the answer_id's zero-indexed.
        try:
            answer = int(batch[headers['Answer.Q' + str(answer_index) + 'Answer']])
            batch_data[hit_id]['answers'][answer_id - 1].append(answer)
        except:
            # print('Invalid input: ' + str(batch[headers['Answer.Q' + str(answer_index) + 'Answer']]()))
            pass

def save_human_answers():
    # Save human answers.
    with open(human_answers_outfile, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        for hit_id in batch_data:
            if 'true answers' not in batch_data[hit_id]:
                continue
            csvwriter.writerow([str(hit_id)] + batch_data[hit_id]['true answers'])

def input_human_answers():
    for hit_id in batch_data:
        batch_data[hit_id]['true answers'] = []
        for answer_id, answer in enumerate(batch_data[hit_id]['answers']):
            print batch_data[hit_id]['questions'][answer_id]
            true_answer = raw_input('Answer: ')
            if true_answer not in ['-1', '0', '1']:
                return save_human_answers()
            true_answer = int(true_answer)
            batch_data[hit_id]['true answers'].append(true_answer)
    return save_human_answers()

# Input new human answers.
if INPUT_HUMAN_ANSWERS:
    input_human_answers()

# Analyze batch results.
sum_square_error = 0.0
num_answers = 0
num_answered_opposite = 0
num_answered_same = 0
num_answered_different = 0
num_not_enough_answers = 0
answer_breakdown_count = {}
for hit_id in batch_data:
    for answer_id, answer in enumerate(batch_data[hit_id]['answers']):
        if len(answer) < 2:
            num_not_enough_answers += 1
            continue

        if USE_FIRST_TWO_ANSWERS_ONLY:
            answer = answer[0:2]

        if (max(answer) - min(answer)) == 2:
            num_answered_opposite += 1
            continue
        mean_answer = sum(answer) / len(answer)

        answer_tuple = tuple(sorted(answer))
        if answer_tuple not in answer_breakdown_count:
            answer_breakdown_count[answer_tuple] = 0
        answer_breakdown_count[answer_tuple] += 1

        square_error = 0.0
        for answer_i in answer:
            square_error += (answer_i - mean_answer)**2
            num_answers += 1
        if square_error > 0:
            # print str(answer) + '\t' + batch_data[hit_id]['questions'][answer_id]
            sum_square_error += square_error
            num_answered_different += 1
        else:
            num_answered_same += 1
            # print str(answer) + '\t' + batch_data[hit_id]['questions'][answer_id]


rmse = (sum_square_error / num_answers)**0.5
print('RMSE: %f' % rmse)
print('Num answers: %d' % num_answers)
print('Num sentences answered opposite: %d' % num_answered_opposite)
print('Num sentences answered same: %d' % num_answered_same)
print('Num sentences answered different : %d' % num_answered_different)
print('Num sentences only one answer: %d' % num_not_enough_answers)
print('Answer breakdown: ' + str(answer_breakdown_count))

if WRITE_OUTPUT_CSV:
    with open(turk_answers_outfile, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        for hit_id in batch_data:
            for answer_id, answer in enumerate(batch_data[hit_id]['answers']):
                if len(answer) < 2:
                    continue
                # For consistency, only use the first two answers to each question.
                if USE_FIRST_TWO_ANSWERS_ONLY:
                    answer = answer[0:2]

                # Remove sentences with opposite answers.
                if (max(answer) - min(answer)) == 2:
                    continue

                csv_writer.writerow([batch_data[hit_id]['questions'][answer_id], sum(answer)/float(len(answer))])
