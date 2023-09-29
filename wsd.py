# AIT 526
# Word Sense Disambiguation Assignment
# 09/27/2023
# Jeffrey Stejskal, Devin Schechter, Stuti Tandon, Abiha Abbas

# Explanation
# This program is meant to perform word sense disambiguation using decision lists. This invovles predicting the correct sense of a word where a word may have more than one meaning.
# This application in particular is meant to classify words into either the "product" or "phone" line categories using conditional probability.

# Instructions
# This program must be run from the command line. To execute this program please enter the following code.
# python decision-list.py line-train.xml line-test.xml my-decision-list.txt > my-line-answers.txt
# This code may then be followed with the command below to execute the scorer program to evaluate this model's accuracy.
# python scorer.py my-line-answers.txt line-answers.txt >wsdreport.txt

# Example Output:
# This code will output a file that contains information that resemble the below:
# <answer instance="line-n.w8_059:8174:" senseid="product"/>
# <answer instance="line-n.w7_098:12684:" senseid="phone"/>
# <answer instance="line-n.w8_106:13309:" senseid="phone"/>


# Import Packages
import re
import sys
from bs4 import BeautifulSoup
import math


#input files
training_file = sys.argv[1] 
testing_file = sys.argv[2]
output_file = sys.argv[3]


# Open Data
def open_file(filename):
    y=open(filename)
    data=y.read()
    parser = BeautifulSoup(data, 'xml')
    
    return parser


# Create counter function for probability calculation
def counter(text,attribute):
    count = 0
    
    for line in text:
        if line is not None and attribute(line)[0]:
            count = count +1

    return count


# Function to calculate the probability of each sense
def get_probability(attribute):
        
        # Sense and other text are considered phone_sense input.
        sense_text = phone_sense 
        other_text = phone_sense

        sense = attribute('')[1] 
        if sense == 'product':
            sense_text = product_sense
            other_text = phone_sense

        # Get counts
        sense_count = counter(sense_text,attribute)
        other_count = counter(other_text,attribute)
        total_count = sense_count + other_count  
        prob_sense = sense_count / total_count  
        prob_other = other_count / total_count 
        
        #Calculate the probability using log (if 0 -> replace with 1)
        try:
            ratio = math.log10(prob_sense / prob_other)
        except ZeroDivisionError:
            ratio = 1
        
        # output the logliklihoods to the output file
        with open(output_file, 'a+') as output:
            output.write(f'{attribute.__name__}\t{ratio}\t{sense}\n')

        return ratio


# Create Set of Features for the decision list

def features():

    def market(line):
        return (re.search(r'\b[Mm]arkets?\b', line), 'product')
    yield market

    def analyst(line):
        return ('analyst' in line, 'product')
    yield analyst

    def sales(line):
        return (re.search(r'\b[sS]ales?\b',line),'product')
    yield sales
    
    def dealer(line):
        return (re.search(r'\b[dD]ealers?\b', line), 'product')
    yield dealer
    
    def network(line):
        return (re.search(r'\b[nN]etworks?\b', line), 'product')
    yield network

    def price(line):
        return (re.search(r'\b[pP]rices?\b', line), 'product')
    yield price
    
feature_list = [feature for feature in features()]

if __name__ == '__main__':  

    # Open and read the training file
    parser = open_file(training_file)
    
    # Create place holiders for phone senses and product senses
    phone_sense = [] 
    product_sense = [] 
   
   # Loop through all instances found in the parser and determine if it is a "phone" or "product"
    for instance in parser.find_all('instance'):
        # If the senseid is a phone
        if instance.answer['senseid'] == 'phone':
            for tag in instance.find_all('s'): 
                string = tag.string
                phone_sense.append(string)
        # Otherwise, set treat as a product
        else:
            for tag in instance.find_all('s'):
                string = tag.string
                product_sense.append(string)
                

    feature_list.sort(key=get_probability)

    # Get the number of items identified as product vs phone
    phone = len(parser.find_all(senseid="phone")) 
    product = len(parser.find_all(senseid="product")) 
    default_value = 'phone'

   # Open and read the testing file
    parser = open_file(testing_file)

    # Find and idenfity the senses of each instance     
    for instance in parser.find_all('instance'):
        context = tuple(
                tag.string for tag in instance.find_all('s')
                if tag.string is not None
                )

        sense = None
        for line in context:
            for attribute in feature_list:
                test_result = attribute(line)

                if test_result[0]:
                    sense = test_result[1]
                    break
        # Default to 'phone' if a match isn't found
        if sense is None:
            sense = default_value

        # Print output
        id_num = instance['id']
        print(f'<answer instance="{id_num}" senseid="{sense}"/>')