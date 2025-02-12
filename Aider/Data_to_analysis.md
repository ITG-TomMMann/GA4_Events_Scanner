
High-Level Objective
•	Create a command line for python that as input takes a location to csv data, a locaiton of .md hypothesis and outputs a an analytical email by analysing the data using the hypothesis. 

Mid-Level Objective
•	I want a command line tool where I specify the file like data.csv (contains web data) and a hypothesis with which to answer 
•	The data should be transformed into the correct format and aggregated according to what's necessary 
•	The output should answer the hypothesis, provide evidence to back up the points using data in the style of an analytical email

Implementation Notes
•	Make sure to write the analytical email for the JLR client but coming from perspecitve of Tom the analyst
•	Parsing inputs as file links and outputting the email version into a folder named after the inputted csv
•	MAke sure to write python unit and other tests for making sure that data is passed correctly. Data will be passed as csv format and needs to be transformed first
•	The data transformation should be first scoped by o1 model and executed by the 4o model. The plan needs to be solely formed by o1, breaking down the analysis into multiple steps and then executing it. 
•	Make sure to store prompts as .md in order to enable versioning, tracing via langsmith, and iterative improvemnets 

Context
Beginning context
•	data_to_analysis/main.py 

Ending context
•	data_to_analysis/main.py 
•	data_to_analysis/output_data/analytical_email.md
•	data_to_analysis/aggregated_data/processed_data.csv
•	data_to_analysis/processed_hypothesis/processed_hypothesis.md



Low-Level Tasks
Ordered from start to finish 

1.	[First task - what is the first task?]
CREATE aider """
Create a cmd script which takes in (location to csv data, location to .md hypothesis)
It outputs an anlytical email (data_to_analysis/output_data/analytical_email.md),
processed_data  data_to_analysis/aggregated_data/analytical_email.md
and the processed data_to_analysis/processed_hypothesis/processed_hypothesis.md

 
This functions makes calls to hypothesis_processor to process the hypothesis which is then used for the

"""


2.	[Second task - what is the second task?]
CREATE aider """
Create hypothesis_processor(.md file location) -> processed_hypothesis.md 
which takes the .md file and outputs a details process of analysing the data in .md format to further process the data

eg. .md contains the following hyptohesis: The classic defender configruator has a higher enquiry/config completion rate than defender configurator. Why could this be?

The funciton needs to: 
1. Outline that we need to compare the performance of defender vs classic defender. 
2. Aggregate the data to compare the two config types
3. Define what enquiry and config completion rate is, in this case the definition is enquiries/ total visitors
4. Compare the two values according to the hypothesis and answer it. 
This function is called form within task 1 function (Cmd script) 


"""

3.	[Third task - what is the third task?]
AIDER CREATE """
Create a process_data(.csv location) -> processed data according to the processed hypothesis specificaiton
Transform the csv data according the requimrents and output processed data in 
data_to_analysis/aggregated_data/processed_data.csv
This function is called form within task 1 function (Cmd script)
"""


"""

4.	[Third task - what is the third task?]
AIDER CREATE """
Create funciton which takes processed hypothesis and processed data -> analytical email 
Once the process data and hypothesis processor have processed 
output an analytical email as part of the cmd script  
This function is called form within task 1 function (Cmd script) and depends on procss_data and process_hyptoehsis 
"""


"""



5.	[Third task - what is the third task?]
AIDER CREATE """
Create langsmith tracing for the various API calls 

"""
