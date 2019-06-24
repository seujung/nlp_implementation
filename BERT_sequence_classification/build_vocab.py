import pandas as pd
import itertools
import pickle
import gluonnlp as nlp
from pathlib import Path
from mecab import MeCab
from model.utils import Vocab
from collections import Counter

# loading dataset
cwd = Path.cwd()
tr_path = cwd / 'data' / 'train.txt'
tr = pd.read_csv(tr_path, sep='\t').loc[:, ['document', 'label']]

# extracting morph in sentences
split_fn = MeCab().morphs
list_of_tokens = tr['document'].apply(split_fn).tolist()

# making the vocab
min_freq = 10
token_counter = Counter(itertools.chain.from_iterable(list_of_tokens))
list_of_tokens = list(map(lambda elm: elm[0], filter(lambda elm: elm[1] >= 10, token_counter.items())))
list_of_tokens = sorted(list_of_tokens)
list_of_tokens.insert(0, '<pad>')
list_of_tokens.insert(0, '<unk>')

tmp_vocab = nlp.Vocab(counter=Counter(list_of_tokens), min_freq=1, bos_token=None, eos_token=None)

# connecting SISG embedding with vocab
ptr_embedding = nlp.embedding.create('fasttext', source='wiki.ko')
tmp_vocab.set_embedding(ptr_embedding)
array = tmp_vocab.embedding.idx_to_vec.asnumpy()

vocab = Vocab(list_of_tokens, padding_token='<pad>', unknown_token='<unk>', bos_token=None, eos_token=None)
vocab.embedding = array

# saving vocab
with open('./data/vocab.pkl', mode='wb') as io:
    pickle.dump(vocab, io)