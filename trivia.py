from easy_elasticsearch import ElasticSearchBM25
import json
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['docker', 'executable', 'existing'], default='docker', help='What kind of ES service')
parser.add_argument('--query')
mode = parser.parse_args().mode
query = parser.parse_args().query

df = pd.read_csv('https://query.data.world/s/uvgoxvgmkio7gvhfguql3ohlun2iys', encoding = "ISO-8859-1")
df.index.name="qid"

max_corpus_size = 100000

all_questions = {}
all_answers = {}

for index, row in df.iterrows():
    all_questions[index] = row['Question']
    if len(all_questions) >= max_corpus_size:
        break
    all_answers[index] = row['Answer']
    if len(all_answers) >= max_corpus_size:
        break

qids = list(all_questions.keys())
questions = [all_questions[qid] for qid in qids]
print('|questions|:', len(questions))
print('|words|:', len([word for q in questions for word in q.split()]))

if mode == 'docker':
    bm25 = ElasticSearchBM25(dict(zip(qids, questions)), port_http='9222', port_tcp='9333', service_type='docker')
elif mode == 'executable':
    bm25 = ElasticSearchBM25(dict(zip(qids, questions)), port_http='9222', port_tcp='9333', service_type='executable')
else:
    # Or use an existing ES service:
    assert mode == 'existing'
    bm25 = ElasticSearchBM25(dict(zip(qids, questions)), host='http://localhost', port_http='9200', port_tcp='9300')

rank = bm25.query(query, topk=10)  # topk should be <= 10000
scores = bm25.score(query, document_ids=list(rank.keys()))
answers = [all_answers[int(qid)] for qid in list(rank.keys())]

print('> Query:', query)
print('> Rank:', json.dumps(rank, indent=4))
print('> Answers:', json.dumps(answers, indent=4))
print('> Rank Scores:', json.dumps(scores, indent=4))

bm25.delete_index()  # delete the one-trial index named 'one_trial'
if mode == 'docker':
    bm25.delete_container()
elif mode == 'executable':
    bm25.delete_excutable()