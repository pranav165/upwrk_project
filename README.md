# upwrk_project

Task 1 - Scrape url for data

Steps

1) Start python web server - python -m http.server 8000

2) Run python task1.py

Works on Chrome version 108

Task 2

Hi , I want a console python app very simple, $200
Create a python console app which is made up of sender and reviever .
Sender will send a payload which looks like this

{
  timeSlotId= "XXXXXXXXX"
  date = "xxxxxx"
}



When rhe receiver reviews this they provide an answer either accept or reject



The message Is sent back to the sender like this



{
  timeSlotId = "XXXXXXXXX"
  answer = "reject" or "accept"
  date = "xxxxxx"
}



If the answer is reject we store in Aws redis so next time we won't send receiver Same timeSlotId



The sender should print the payload answer for now , next piece of work we will deal with proper functionality



Use aws sqs for communication between sender and receiver