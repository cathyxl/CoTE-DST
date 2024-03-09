import os
import json
import copy
from glob import glob
import argparse
# from utils import get_predicted_slot_value


def get_predicted_slot_value(output_sent, method="cot"):
    if output_sent.lower().startswith("there is no answer"):
        output_sent = "NONE"
    if method.startswith("cot"):
        return output_sent.split(",")[0].strip()
    return output_sent

"generate dummy out for generated texts"

sgd_idx_convert = {0:0, 5:1, 9:2, 13:3, 15:4, 17:5, 19:6, 22:7, 23:8, 24:9, 26:10, 29:11, 30:12, 33:13, 35:14, 37:15, 38:16, 41:17, 42:18, 43:19, 44:20}

def main(args):
    if args.dataset.startswith("multiwoz") or args.dataset == "sgd" or args.dataset == "dstc2":
        if args.dataset == "multiwoz2.2":
            # create dummy frame as in MultiWOZ2.2 file format
            domains = {"train": 0, "taxi":1, "bus":2, "police":3, "hotel":4, "restaurant":5, "attraction":6, "hospital":7}
            # skip domains that are not in the testing set
            excluded_domains = ["police", "hospital", "bus"]
        elif args.dataset == "multiwoz2.0" or args.dataset == "multiwoz2.1" or args.dataset == "multiwoz2.4":
            # create dummy frame as in MultiWOZ2.2 file format
            domains = {"hotel": 0, "train": 1, "attraction": 2, "restaurant": 3, "taxi": 4, "bus": 5, "hospital": 6}
            # skip domains that are not in the testing set
            excluded_domains = ["hospital", "bus"]
        elif args.dataset == "sgd":
            domains = {
                        'Alarm_1': 0, 'Buses_3': 5, 'Events_3': 9, 'Flights_4': 13, 'Homes_2': 15,
                        'Hotels_2': 17, 'Hotels_4': 19, 'Media_3': 22, 'Messaging_1': 23, 'Movies_1': 24,
                        'Movies_3': 26, 'Music_3': 29, 'Payment_1': 30, 'RentalCars_3': 33, 'Restaurants_2': 35,
                        'RideSharing_2': 37, 'Services_1': 38, 'Services_4': 41,
                        'Trains_1': 42, 'Travel_1': 43, 'Weather_1': 44
                    }
            # skip domains that are not in the testing set
            excluded_domains = []
        elif  args.dataset == "dstc2":
            domains = {"restaurant": 0}
            excluded_domains = []
        else:
            print("Exception! Exiting!")
            exit(-998)

        dummy_frames = []
        for domain, d_id in domains.items():
            # if domain in excluded_domains:
            #     continue
            dummy_frames.append({"service": domain, "state": {"slot_values": {}}})

        # Create dummy jsons to fill in later
        dummy_dial_file_jsons = {}
        split = "test"
        target_jsons = glob(os.path.join(args.data_dir, "{}/*json".format(split)))
        for target_json_n in target_jsons:
            if target_json_n.split("/")[-1] == "schema.json":
                continue
            filename = target_json_n.split("/")[-1]
            dummy_dial_file_json = []
            target_json = json.load(open(target_json_n))
            for dial_json in target_json:
                dial_id = dial_json["dialogue_id"]
                dummy_dial_json = {"dialogue_id": dial_id, "turns":[]}

                for turn_idx, turn in enumerate(dial_json["turns"]):
                    try:
                        turn_id = turn["turn_id"]
                    except KeyError:
                        turn_id = turn_idx
                    if turn["speaker"] == "USER":
                        dummy_dial_json["turns"].append({"turn_id": turn_id, "speaker": "USER", "frames": copy.deepcopy(dummy_frames)})
                    else:
                        dummy_dial_json["turns"].append(turn)

                dummy_dial_file_json.append(dummy_dial_json)
            dummy_dial_file_jsons.update({filename: dummy_dial_file_json})

        idx_lines = open(args.test_idx).readlines()
        out_lines = open(args.prediction_txt).readlines()

        # fill out dummy jsons with parsed predictions
        for _idx in range(len(idx_lines)):
            idx_list = idx_lines[_idx].strip()
            dial_json_n, dial_idx, turn_idx, frame_idx, d_name, s_name = idx_list.split("|||")

            val = out_lines[_idx].strip()
            # For active slots, update values in the dummy jsons
            if val != "NONE":
                try:
                    predicted_val = get_predicted_slot_value(val, method=args.method).strip()
                    
                    if predicted_val == "NONE":
                        continue
                except:
                    print(f"idx={_idx} output with invalid format, skipping...")
                    continue
                d_s_name = d_name + "-" + s_name
                if args.dataset == "sgd":
                    frame_idx = sgd_idx_convert[int(frame_idx)]
                dummy_dial_file_jsons[dial_json_n][int(dial_idx)]["turns"][int(turn_idx)]["frames"][int(frame_idx)]["state"]["slot_values"].update({d_s_name: [predicted_val]})
            # NONE token means the slot is non-active. Skip the updating option
            else:
                continue

        if not os.path.exists(args.out_dir):
            os.mkdir(args.out_dir)
        for dial_json_n, dummy_dial_file_json in dummy_dial_file_jsons.items():
            with open(os.path.join(args.out_dir, f"dummy_out_{dial_json_n}"), "w") as dummy_out_file:
                json.dump(dummy_dial_file_json, dummy_out_file, indent=4)

    else:
        # dataset formalized to multiwoz 2.2 style
        if args.dataset.startswith("m2m-R-M"):
            domains = ["restaurant", "movies"]
        elif args.dataset == "m2m-R":
            domains = ["restaurant"]
        elif args.dataset == "m2m-M":
            domains = ["movies"]
        elif args.dataset.startswith("woz2.0"):
            domains = ["restaurant"]
        # elif args.dataset == "dstc2":
        #     domains = ["restaurant"]
        else:
            print("Exception! Exiting!")
            exit(-998)

        dummy_frames = []
        for domain in domains:
            dummy_frames.append({"service": domain, "state": {"slot_values": {}}})
        dummy_dial_file_json = []
        target_json = json.load(open(os.path.join(args.data_dir, "test.json")))
        for dial_json in target_json:
            dial_id = dial_json["dialogue_id"]
            dummy_dial_json = {"dialogue_id": dial_id, "turns": []}

            for turn in dial_json["turns"]:
                turn_id = turn["turn_id"]
                if turn["speaker"] == "USER":
                    dummy_dial_json["turns"].append({"turn_id": turn_id, "speaker": "USER", "frames": copy.deepcopy(dummy_frames)} )
                else:
                    dummy_dial_json["turns"].append(turn)

            dummy_dial_file_json.append(dummy_dial_json)

        idx_lines = open(args.test_idx).readlines()
        out_lines = open(args.prediction_txt).readlines()

        # fill out dummy jsons with parsed predictions
        for _idx in range(len(idx_lines)):
            idx_list = idx_lines[_idx].strip()
            dial_json_n, dial_idx, turn_idx, frame_idx, d_name, s_name = idx_list.split("|||")

            val = out_lines[_idx].strip()
            # For active slots, update values in the dummy jsons
            if val != "NONE":
                try:
                    predicted_val = get_predicted_slot_value(val).strip()  # if there is no answer, change to NONE
                    if predicted_val == "NONE":
                        continue
                except:
                    print(f"idx={_idx} output with invalid format, skipping...")
                    continue
                d_s_name = d_name + "-" + s_name
                dummy_dial_file_json[int(dial_idx)]["turns"][int(turn_idx)]["frames"][int(frame_idx)]["state"]["slot_values"].update({d_s_name: [predicted_val]})
            # NONE token means the slot is non-active. Skip the updating option
            else:
                continue

        if not os.path.exists(args.out_dir):
            os.mkdir(args.out_dir)

        with open(os.path.join(args.out_dir, "dummy_out.json"), "w") as dummy_out_file:
            json.dump(dummy_dial_file_json, dummy_out_file, indent=4)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./MultiWOZ_2.2/")
    parser.add_argument("--out_dir", type=str, default="./MultiWOZ_2.2/dummy/")

    parser.add_argument("--test_idx", type=str, default="./MultiWOZ_2.2/test.idx")
    parser.add_argument("--prediction_txt", type=str, default="")
    parser.add_argument("--method", type=str, default="cot", choices=["cotqa", "sdp", "cot"])
    parser.add_argument("--dataset", type=str, default="multiwoz2.2",
                        choices=["multiwoz2.2","multiwoz2.4", "multiwoz2.1", "multiwoz2.0", "m2m-R-M",  "m2m-R-M-full", "m2m-R", "m2m-M", "woz2.0", "woz2.0-simple","dstc2", "sgd"])
    args = parser.parse_args()

    main(args)
                                                                             