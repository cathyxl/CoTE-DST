import os
import sys
import json
from glob import glob
from random import sample

domain_desc_flag = True # To append domain descriptions or not 
slot_desc_flag = True  # To append slot descriptions or not 
PVs_flag = True # for categorical slots, append possible values as suffix

def preprocess(dial_json, schema, out, idx_out, excluded_domains, frame_idxs, split):
  dial_json_n = dial_json.split("/")[-1]
  dial_json = open(dial_json)
  dial_json = json.load(dial_json)
  for dial_idx in range(len(dial_json)):
    dial = dial_json[dial_idx]
    cur_dial = ""
    for turn in dial["turns"]:
      speaker = " [" + turn["speaker"] + "] " 
      uttr = turn["utterance"]
      cur_dial += speaker
      cur_dial += uttr  

      if turn["speaker"] == "USER":
        active_slot_values = {}
        for frame_idx in range(len(turn["frames"])):
          frame = turn["frames"][frame_idx]
          for key, values in frame["state"]["slot_values"].items():
            value = sample(values,1)[0]
            active_slot_values[key] = value

        # iterate thourgh each domain-slot pair in each user turn 
        for domain in schema:
          # skip domains that are not in the testing set
          if domain["service_name"] in excluded_domains:
            continue
          slots = domain["slots"]
          for slot in slots:
            d_name, s_name = slot["name"].split("-")
            # generate schema prompt w/ or w/o natural langauge descriptions
            schema_prompt = ""
            schema_prompt += " [domain] " + d_name + " " + domain["description"] if domain_desc_flag else d_name
            schema_prompt += " [slot] " + s_name + " " + slot["description"] if slot_desc_flag  else s_name
            if PVs_flag:
              # only append possible values if the slot is categorical
              if slot["is_categorical"]:
                PVs = ", ".join(slot["possible_values"])
                schema_prompt += " [PVs] " + PVs

            if slot["name"] in active_slot_values.keys():
              target_value = active_slot_values[slot["name"]]
            else:
              # special token for non-active slots
              target_value = "NONE"
            
            line = { "dialogue": cur_dial + schema_prompt, "state":  target_value }
            out.write(json.dumps(line))
            out.write("\n")

            # write idx file for post-processing deocding
            idx_list = [ dial_json_n, str(dial_idx), turn["turn_id"], str(frame_idxs[d_name]), d_name, s_name ]
            idx_out.write("|||".join(idx_list))
            idx_out.write("\n")
  return


def get_predicted_slot_value(output_sent):
    return output_sent.split(",")[0].strip()