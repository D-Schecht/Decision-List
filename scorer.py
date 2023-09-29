# AIT 526
# Word Sense Disambiguation Assignment (scorer funciton)
# 09/27/2023
# Jeffrey Stejskal, Devin Schechter, Stuti Tandon, Abiha Abbas

# Explanation
# This program is meant to evaluate the accuracy of the wsd.py script outputs. A confusion matrix and accuracy score are returned.

# Instructions
# This code is preceded by the execution of the wsd.py file and is executed using the following command line prompt
# python scorer.py my-line-answers.txt line-answers.txt >wsdreport.txt

# Example Output:
# This code will output a file that contains information that resemble the below:
# The accuracy score For this model was: 64.0 
# followed by a confusion matrix

# Import Packages
import sys
import pandas as pd
from nltk.metrics import ConfusionMatrix


# Create a function to read and process the output/key files
def process_file(input_file):
    # Open the file and identify key value pairs
    with open(input_file) as file: 
        f = [line.rstrip('\n') for line in file] 
        vars = [i.split(':"', 1) for i in f]
        vars_dict = {}

    # Loop through the instance ids and create a dict that stores the id and sense as a key-value pair
    for idx in range (1,len(vars)): 
        key = vars[idx][0]
        value = vars[idx][1]
        vars_dict[key] = value

   # Loop through vars_dict and add the values to vars_list
    vars_list=[]                   
    for val in vars_dict:
        vars_list.append(vars_dict[val])
    
    return vars_list


# Create the score function
def score():

    # Read in data files (output file and key file)
    output_file = sys.argv[1]
    key_file = sys.argv[2] 

    # Process prediction and key files
    predicted_list = process_file(output_file)
    key_list = process_file(key_file)

    # Calculate Confusion Matrix
    cm=ConfusionMatrix(key_list,predicted_list) 

    # Calculate Accuracy
    count=0
    for i in range(len(predicted_list)):

        if predicted_list[i] == key_list[i]:  
            count += 1

    accuracy = (count/len(predicted_list)*100)

	# Print the confusion matrix and accuracy values to the wsdreport.txt file
    print('The accuracy score For this model was:',accuracy,'\n\n''Confusion Matrix: ',str(cm),)


    
if __name__ == '__main__':
    score()