import enum
import os
import sys
import json
from glob import glob
from tqdm import tqdm
import string

domain_desc_flag = True # To append domain descriptions or not 
slot_desc_flag = True  # To append slot descriptions or not 
PVs_flag = True # for categorical slots, append possible values as suffix

change_dict = {
    "What's the what is the type of the hotel?": "What's the type of the hotel?",
    "What's the whether the hotel has parking?": "Does the hotel have parking?",
    "What's the length of stay at the hotel?": "How long is the stay at the hotel?",
    "What's the whether the hotel has internet?": "Does the hotel have internet?",
    "What's the area or place of the hotel?": "Which area is the hotel in?",
    "What's the how many train tickets you need?": "How many train tickets do you need?",
    "What's the how much is the entrance fee?": "How much is the entrance fee?",
    "What's the area or place of the restaurant?": "Which area is the restaurant in?",
    "What's the the phone number of the restaurant?": "What's the phone number of the restaurant?",
    "What's the the cuisine of the restaurant you are looking for?": "What cuisine are you looking for at the restaurant?",
    "What's the how many people for the restaurant reservation?": "How many people are there for the restaurant reservation?",
    "What's the number of people for the hotel booking?": "How many people are there for the hotel booking?",
    "What's the parking facility at the hotel?": "Does the hotel have parking?",
    "What's the number of people booking for train?": "How many people are there for booking the train?",
    "What's the area or place of the attraction?": "Which area is the attraction in?",
    "What's the number of people booking the restaurant?": "How many people are there for booking the restaurant?",
    "What's the time of the restaurant booking?": "When is the time of the restaurant booking?",
    "What's the number of people booking bus tickets?": "How many people are there for booking bus tickets?",
    "What's the number of people going to the restaurant?": "How many people are there going to the restaurant?",
    "What's the number of people watching the movie?": "How many people are there watching the movie?",
}

def preprocess(dial_json, schema, out, idx_out, excluded_domains, frame_idxs, split):
    dial_json_n = dial_json.split("/")[-1]
    dial_json = open(dial_json)
    dial_json = json.load(dial_json)
    for dial_idx in tqdm(range(len(dial_json))):
        dial = dial_json[dial_idx]
        cur_dial = ""

        related_map = {}    # {key1: [(uttr1, value1), (uttr2, value2), ...], key2: [...]}

        for turn_idx, turn in enumerate(dial["turns"]):
            # speaker = " [" + turn["speaker"] + "] "
            speaker = " The user: " if turn["speaker"] == "USER" else " The system: "
            uttr = turn["utterance"]
            cur_dial += speaker
            cur_dial += uttr

            if turn["speaker"] == "USER":
                active_slot_values = {}
                for frame_idx in range(len(turn["frames"])):
                    frame = turn["frames"][frame_idx]
                    for key, values in frame["state"]["slot_values"].items():
                        # if have multiple answers, select the last one
                        value = values[-1]
                        active_slot_values[key] = value
                        # if the value first appears or different from the last one, then mark this as keysent
                        if key not in related_map or value != related_map[key][-1][-1]:
                            tmp_list = related_map.get(key, [])
                            # 0902: add previous system utterance too
                            prev_uttr = dial["turns"][turn_idx - 1]["utterance"] if turn_idx > 0 else "###NULL###"
                            tmp_list.append((prev_uttr, uttr, value))
                            related_map.update({key: tmp_list})

                # iterate through each domain-slot pair in each user turn
                for domain in schema:
                    # skip domains that are not in testing set
                    if domain["service_name"] in excluded_domains:
                        continue
                      
                    slots = domain["slots"]
                    for slot in slots:
                        # modify the schema into Multiple-Choice questions
                        # 1. if contain *possible values*, switch into MCQs.
                        # 2. if not contain, switch into common QAs. 

                        schema_prompt = "Answer the question based on the dialogue between the user and the system."

                        d_name, s_name = slot["name"].split("-")
                        # don't consider domain
                        schema_prompt += " | Question: "
                        
                        question = f"What's the {slot['description']}?"
                        question = change_dict.get(question, question)

                        schema_prompt += question

                        if PVs_flag and slot["is_categorical"]:
                            # only append possible values if the slot is categorical
                                schema_prompt += " | Choices:"
                                choices = slot["possible_values"]
                                for cho, cap in zip(choices, string.ascii_uppercase[:len(choices)]):
                                    schema_prompt += f" ({cap}) {cho}"
                        
                        schema_prompt += " | Dialogue:"
                        schema_prompt += cur_dial
                        
                        if slot["name"] in active_slot_values.keys():
                            target_value = active_slot_values[slot["name"]]
                            # related utterances for reasoning
                            related_uttrs = related_map.get(slot["name"], [])
                            ## placing the answer at the front. 
                            chain_of_thought = "because there is a dialogue between the user and the system: "
                            tmp = []
                            for ut in related_uttrs:
                                thought = f'" The system: {ut[0]}' if ut[0] != "###NULL###" else '"'
                                thought += f' The user: {ut[1]}"'
                                tmp.append(thought)
                            chain_of_thought += ", and ".join(tmp)
                            target_value = f"{target_value}, {chain_of_thought}."

                            # target_value = target_value.strip(string.punctuation)
                        else:
                            # target_value = "NONE"
                            target_value = "There is no answer."
                        
                        line = {"dialogue": schema_prompt, "result": target_value}
                        out.write(json.dumps(line))
                        out.write("\n")

                        # write idx file for post-processing decoding
                        idx_list = [ dial_json_n, dial_idx, turn["turn_id"], frame_idxs[d_name], d_name, s_name ]
                        idx_out.write("|||".join([str(item) for item in idx_list]))
                        idx_out.write("\n")


def get_predicted_slot_value(output_sent):
    if output_sent.lower().startswith("there is no answer"):
        return "NONE"
    return output_sent

