#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import sys
from bs4 import BeautifulSoup
from nltk.util import ngrams
from nltk import ConditionalFreqDist
from nltk.stem.snowball import SnowballStemmer
from nltk.probability import ConditionalProbDist, ELEProbDist
from collections import defaultdict


# In[2]:


def process_xml_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'xml')
    return soup


# In[3]:


def preprocess_data(soup):
    instances = soup.find_all('instances')
    data_dict = {}
    
    for instance in instances:
        instance_id = instance['id']
        answer = instance.find('answer')
        if answer:
            sense = answer['senseid']
        else:
            sense = " "
        context = instance.context.get_text()
        
        context = context.lower()
        context = re.sub(r'[^\w\s]', '', context)
        
        tokens = context.split()
        stemmer = SnowballStemmer('english')
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        context = ' '.join(stemmed_tokens)
        
        data_dict[instance_id] = {'sense': sense, 'tokens': stemmed_tokens}
    return data_dict


# In[4]:


def create_decision_list(train_data):
    cfdist = ConditionalFreqDist()
    
    for instance_id, data in train_data.items():
        sense = data['sense']
        tokens = data['tokens']
        
        for i, token in enumerate(tokens):
            if token == 'line':
                left_tokens = tokens[i - 2:i] if i >= 2 else tokens[:i]
                right_tokens = tokens[i + 1:i + 2]
                
                for lt in left_tokens:
                    cfdist[sense][lt] += 1
                for rt in right_tokens:
                    cfdist[sense][rt] += 1
                    
    cpdist = ConditionalProbDist(cfdist, ELEProbDist, bins = 290)
    print(cpdist['run'].max)
    print(cpdist['run'].prob('NN'))
    
    pdists= {}
    for sense in cfdist:
        fd = cfdist[sense]
        pd = ELEProbDist(fd)
        pdists[sense] = pd
        
    for sense, freqdist in cfdist.items():
        print(f"Senses: {sense}")
        for word, freq in freqdist.itmes():
            print(f"\tWord: {word} Frequency: {freq}")
    
    return cfdist


# In[5]:


def apply_decision_list(decision_list, test_data, predicted_labels_file):
    predicted_labels = {}
    
    for instance_id, data in test_data.items():
        tokens = data['tokens']
        label = None
        max_freq = 0
        
        for sense, freqdist in decision_list.items():
            freq = 0 
            for token in tokens:
                freq += freqdist[token]
            if freq > max_freq:
                label = sense
                max_freq = freq
                
        predicted_labels[instance_id] = label
    
    with open(predicted_labels_file, 'w') as f:
        for instance_id, label in predicted_labels.items():
            f.write(f"{instance_id} {label}\n")
          
    return predicted_labels


# In[6]:


def main(train_file, test_file, decision_list_file, predicted_labels_file):
    train_soup = process_xml_file(train_file)
    test_soup = process_xml_file(test_file)
    
    train_data = preprocess_data(train_soup)
    test_data = preprocess_data(test_soup)
    
    decision_list = create_decision_list(train_data)
    predicted_labels = apply_decision_list(decision_list, test_data, predicted_labels_file)
    
    with open(decision_list_file, 'w') as f:
        for instnace_id, data in train_data.items():
            sense = data['sense']
            tokens = ' '.join(data['tokens'])
            
            f.write(f'<answer instance =" {instnace_id}" senseid="{sense}"/>\n')


# In[7]:


if __name__ == '__main__':
    
    train_file = 'line-train.xml'
    test_file = 'line-test.xml'
    
    decision_list_file = 'my-line-answers.txt'
    predicted_labels_file = 'my-predicted-labels.txt'
    
    main(train_file, test_file, decision_list_file, predicted_labels_file)


# In[8]:


def read_key_file(key_file):
    key = {}
    with open(key_file, 'r') as f:
        for line in f:
            answer, instance_id, sense = line.strip().split()[0], line.strip().split()[1], line.strip().split()[2]
            key[instance_id[10:-1]] = sense[9:-3]
    return key

def read_tagged_file(tagged_file):
    tagged = {}
    with open(tagged_file,'r') as f:
        for line in f: 
            answer, instance_id, sense = line.strip().split()[0], line.strip().split()[1], line.strip().split()[2]
            tagged[instance_id[10:-1]] = sense[9:-3]
    return tagged


# In[9]:


def evaluate(key, tagged):
    
    confusion_matrix = defaultdict(lambda: defaultdict(int))
    correct = 0
    total = 0
    accuracy = 0.0
    for instance_id, key_sense in key.items():
        tagged_sense = tagged.get(instance_id)
        if not tagged_sense:
            continue
        confusion_matrix[key_sense][tagged_sense] += 1
        if tagged_sense == key_sense:
            correct += 1
            
        total += 1
        if total > 0:
            accuracy = correct / total
    return accuracy, confusion_matrix


# In[10]:


if __name__ == '__main__':
    tagged_file = 'my-line-answers.txt'
    key_file = 'line-answers.txt'
    
    key = read_key_file(key_file)
    tagged = read_tagged_file(tagged_file)
    
    accuracy, confusion_matrix = evaluate(key, tagged)
    print('Accuracy:', accuracy)
    print('Confusion Matrix:')
    for true_label in confusion_matrix:
        row = confusion_matrix[true_label]
        print(true_label, end='\t')
        for predicted_label in row:
            count = row[predicted_label]
            print(count, end='\t')
        print()


# In[ ]:




