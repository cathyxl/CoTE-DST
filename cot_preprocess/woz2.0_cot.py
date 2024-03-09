import enum
import os
import sys
import json
from tqdm import tqdm

domain_desc_flag = True # To append domain descriptions or not 
slot_desc_flag = True  # To append slot descriptions or not 
PVs_flag = True # for categorical slots, append possible values as suffix

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
                        d_name, s_name = slot["name"].split("-")
                        # generate schema prompt w/ or w/o natural language descriptions
                        schema_prompt = ""
                        schema_prompt += " | Domain: " + d_name
                        if domain_desc_flag:
                            schema_prompt += " " + domain["description"]
                        schema_prompt += " | Slot: "
                        if slot_desc_flag:
                            schema_prompt += slot["description"]
                        else:
                            schema_prompt += s_name

                        if PVs_flag:
                            # only append possible values if the slot is categorical
                            if slot["is_categorical"]:
                                PVs = ", ".join(slot["possible_values"])
                                schema_prompt += " | Possible values: " + PVs
                        
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
                            # in MultiWOZ 2.2, directly use description of slot for prompting
                            target_value = f"{target_value}, {chain_of_thought}."
                        else:
                            target_value = "NONE"
                        
                        line = {"dialogue": cur_dial + schema_prompt, "result": target_value}
                        out.write(json.dumps(line))
                        out.write("\n")

                        # write idx file for post-processing decoding
                        idx_list = [ dial_json_n, dial_idx, turn["turn_id"], frame_idxs[d_name], d_name, s_name ]
                        idx_out.write("|||".join([str(item) for item in idx_list]))
                        idx_out.write("\n")


def get_predicted_slot_value(output_sent):
    return output_sent.split(",")[0].strip()
