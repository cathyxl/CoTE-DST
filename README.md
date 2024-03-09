## Project Repo for Chain of Thought Explanation for Dialogue State Tracking
## 1. Training
a. Prepare dataset and environment by following https://github.com/chiahsuan156/DST-as-Prompting

b. Preprocess dataset 
```
./cot_script_server/preprocess.sh
```
c. Training with processed data
```
./cot_script_server/train.sh

```
## 2. Corresponding questions for each slot
| Domain | Slot | QA Prompt |
| --- | --- | --- |
| hotel | pricerange | What’s the price budget of the hotel?|
hotel | type | What’s the type of the hotel?
hotel | parking | Does the hotel have parking?
hotel | bookday | What’s the day of the hotel booking?
hotel | bookpeople | How many people are there for the hotel booking?
hotel | bookstay | How long is the stay at the hotel?
hotel | stars | What’s the star rating of the hotel?
hotel | internet | Does the hotel have internet?
hotel | name | What’s the name of the hotel?
hotel | area | Which area is the hotel in?
hotel | address | What’s the address of the hotel?
hotel | phone | What’s the phone number of the hotel?
hotel | postcode | What’s the postal code of the hotel?
hotel | ref | What’s the reference number of the hotel booking?
train | arriveby | What’s the arrival time of the train?
train | departure | What’s the departure location of the train?
train | day | What’s the day of the train?
train | bookpeople | How many train tickets do you need?
train | leaveat | What’s the leaving time for the train?
train | destination | What’s the destination of the train?
train | trainid | What’s the id of the train?
train | ref | What’s the reference number of the train booking?
train | price | What’s the price of the train?
train | duration | What’s the duration of the travel?
attractions | area | What’s the area to search for attractions?
attractions | name | What’s the name of the attraction?
attractions | type | What’s the type of the attraction?
attractions | entrancefee | How much is the entrance fee?
attractions | openhours | What’s the open hours of the attraction?
attractions | address | What’s the address of the attraction?
attractions | phone | What’s the phone number of the attraction?
attractions | postcode | What’s the postal code of the attraction?
restaurant | pricerange | What’s the price budget for the restaurant?
restaurant | area | Which area is the restaurant in?
restaurant | food | What cuisine are you looking for at the restaurant?
restaurant | name | What’s the name of the restaurant?
restaurant | bookday | What’s the day of the restaurant booking?
restaurant | bookpeople | How many people are there for the restaurant reservation?
restaurant | booktime | When is the time of the restaurant booking?
restaurant | address | What’s the address of the restaurant?
restaurant | phone | What’s the phone number of the restaurant?
restaurant | postcode | What’s the postal code of the restaurant?
restaurant | ref | What’s the reference number of the restaurant booking?
taxi | leaveat | What’s the leaving time of taxi?
taxi | destination | What’s the destination of taxi?
taxi | departure | What’s the departure location of taxi?
taxi | arriveby | What’s the arrival time of taxi?
taxi | type | What’s the car type of the taxi?
taxi | phone | What’s the phone number of the taxi?


## 3. Cases of QA CoTE
As shown in the case in the following table, with the human-language QA-liked input prompt, the model is able to generate the correct answer, while the model with a normal input prompt fails to predict the correct value. In the CoTE-coarse model, the model is not able to correctly understand the requested slot and therefore fails to track the corresponding value, resulting in the output of a wrong answer with some meaningless dialogue utterances. On the contrary, when input with human-language prompts, the model is able to accurately understand what the requested slot is and correctly generates the answer with a brief and precise explanation.
<table>
<thead>
<tr>
<th>CASE</th>
</tr>
</thead>
<tbody>
<tr><td>
<p><b>Dialogue History</b>:<br>
The user: Hello, Can you book me a table at Golden Wok for 11:00 on Friday?<br>
...<br>
The system: The postcode is cb21tt. Are you looking for a taxi from Old Schools to the Golden Wok?<br>
The user: Yes I do. I’d like to make sure I arrive at the restaurant by the booked time. Can you check?<br>
The system: What time do you want to leave?<br>
The user: Actually all you have to do is set the taxi so it arrives by the arrived time. Am I better off booking it myself?<br>
The system: I have booked you a taxi for Friday to arrive at Old Schools at 10:45. Is there anything else I may help you with?<br>
The user: Thanks for the service, good day.<br>
</td></tr>
</p>

<tr><td>
<p><b>Dialogue Domain:</b>
    taxi
</p>
</td></tr>


<tr><td>
<p><b>Requested Slot:</b>
    taxi-arriveby
</p>
</td></tr>

<!-- <tr><td>
<p><b>Possible Values:</b>
    Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
</p>
</td></tr> -->


<tr><td>
<p><b>Model Input Prompt:</b><br>
Answer the question based on the dialogue. Question: When will the taxi arrive at
starting point? | Dialogues: The user: Hello, Can you book me a table at Golden Wok for 11:00 on
Friday? ... The system: I have booked you a taxi for Friday to arrive at Old Schools at 10:45. ...
</p>
</td></tr>

<tr><td>
<p><b>Model Outputs:</b><br>
<b><em>CoTE-coarse:</em></b><br>
<b>11:00</b>, because the user asked the system to book a table at Golden Wok for 11:00 on
Friday, the system said the postcode was cb21tt, the user said that she was looking for a taxi from
Old Schools to the Golden Wok, the user said that she would like to make sure she arrived at the
restaurant by the booked time, the system asked if she could check, the user said that she did, the
user said that she would like to make sure she arrived at the restaurant by the booked time, and the
system said that he could check.<br>
<b><em>CoTE-refined:</em></b><br>
<b>10:45</b>, because the system said that he had booked a taxi for Friday to arrive at Old Schools
at 10:45, and the user said that she needed the contact number and car type also.<br>
</p>
</td></tr>
<th></th>
</tbody>
</table>

## 4. Fine-grained Settings
| Dataset      ||  $\phi(step)$ |||$\phi(turn)$|| ||$\psi(step)$||
| :---         |---|---|---|---|---|----|---|---|---|---|
| MultiWOZ2.2  | 1 | 2 | 3 | 0-9 | 10-14 | 15-19 | 20+ | 0-11 | 12-14 | 15+ |
|              | 562 | 391 | 47 | 209 | 326 | 370 | 95 | 243 | 560 | 9 |
| M2M-R+M      | 1 | 2 | 3 | 0-9 | 10-14| 15-19 |20+| 0-7| 8-9| 10+|
|              | 790 | 225| 17| 746| 240| 42| 11| 457| 330| 252|
| WOZ2.0  | 1| 2| 3| 0-5| 6-7| 8-9| 10+| 0-5| 6-7| 8+|
|              | 231| 163| 6 |128| 136| 89| 47| 164| 171| 65|