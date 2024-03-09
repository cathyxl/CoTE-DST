import enum
import os
import sys
import json
from glob import glob
from tqdm import tqdm
from utils import preprocess


def main():
    data_path = sys.argv[1]
    data_bin_path = sys.argv[2]
    dataset_name = sys.argv[3]

    if dataset_name.startswith("multiwoz") or dataset_name == "sgd" or dataset_name == "dstc2":

        for split in ["train", "dev", "test"]:
            if dataset_name == "multiwoz2.2":
                frame_idxs = {"train": 0, "taxi":1, "bus":2, "police":3, "hotel":4, "restaurant":5, "attraction":6, "hospital":7}
                # skip domains that are not in the testing set
                excluded_domains = ["police", "hospital", "bus"]
            elif dataset_name in ["multiwoz2.0", "multiwoz2.1", "multiwoz2.4"]:
                frame_idxs = {"hotel": 0, "train": 1, "attraction": 2, "restaurant": 3, "taxi": 4, "bus": 5, "hospital": 6}
                excluded_domains = ["hospital", "bus"]
            elif dataset_name == "sgd":
                if split == "train": 
                    frame_idxs = {
                        'Banks_1': 1, 'Buses_1': 3, 'Buses_2': 4, 'Calendar_1': 6,
                        'Events_1': 7, 'Events_2': 8, 'Flights_1': 10, 'Flights_2': 11, 
                        'Homes_1': 14, 'Hotels_1': 16, 'Hotels_2': 17, 'Hotels_3': 18,
                        'Media_1': 20, 'Movies_1': 24, 'Music_1': 27, 'Music_2': 28, 
                        'RentalCars_1': 31, 'RentalCars_2': 32, 'Restaurants_1': 34, 
                        'RideSharing_1': 36, 'RideSharing_2': 37, 'Services_1': 38, 'Services_2': 39, 
                        'Services_3': 40, 'Travel_1': 43, 'Weather_1': 44
                    }
                elif split == "dev": 
                    frame_idxs = {
                        'Alarm_1': 0, 'Banks_2': 2, 'Buses_1': 3, 'Events_1': 7,
                        'Flights_3': 12, 'Homes_1': 14, 'Hotels_1': 16, 'Hotels_4': 19, 'Media_2': 21, 
                        'Movies_2': 25, 'Music_1': 27, 'RentalCars_1': 31, 'Restaurants_2': 35,
                        'RideSharing_1': 36, 'Services_4': 41, 'Travel_1': 43, 'Weather_1': 44
                    }
                elif split == "test": 
                    frame_idxs = {
                        'Alarm_1': 0, 'Buses_3': 5, 'Events_3': 9, 'Flights_4': 13, 'Homes_2': 15, 
                        'Hotels_2': 17, 'Hotels_4': 19, 'Media_3': 22, 'Messaging_1': 23, 'Movies_1': 24,
                        'Movies_3': 26, 'Music_3': 29, 'Payment_1': 30, 'RentalCars_3': 33, 'Restaurants_2': 35,
                        'RideSharing_2': 37, 'Services_1': 38, 'Services_4': 41, 
                        'Trains_1': 42, 'Travel_1': 43, 'Weather_1': 44
                    }
                excluded_domains = []
            elif dataset_name == "dstc2":
                frame_idxs = {"restaurant": 0}
                excluded_domains = []
            else:
                raise ValueError("dataset name not found!")


            schema_path = os.path.join(data_path, split, "schema.json")
            schema = json.load(open(schema_path))
            print("--------Preprocessing {} set---------".format(split))
            out = open(os.path.join(data_bin_path, "{}.json".format(split)), "w")
            idx_out = open(os.path.join(data_bin_path, "{}.idx".format(split)), "w")
            print(data_path)
            dial_jsons = glob(os.path.join(data_path, "{}/dialogues*json".format(split)))
            dial_jsons = sorted(dial_jsons, key=lambda name: int(name[-8: -5]))
            print(dial_jsons)
            
            sample_idx = 0
            for dial_json in dial_jsons:
                # sample_idx = 0
                sample_idx = preprocess(sample_idx, dial_json, schema, out, idx_out, excluded_domains, frame_idxs, split)
            idx_out.close()
            out.close()

    else:
        if dataset_name.startswith("m2m-R-M"):
            frame_idxs = {"restaurant": 0, "movies": 1}
            excluded_domains = []
        elif dataset_name.startswith("m2m-R"):
            frame_idxs = {"restaurant": 0}
            excluded_domains = []
        elif dataset_name == "m2m-M":
            frame_idxs = {"movies": 0}
            excluded_domains = []
        elif dataset_name.startswith("woz2.0"):
            frame_idxs = {"restaurant": 0}
            excluded_domains = []
        elif dataset_name == "dstc2":
            frame_idxs = {"restaurant": 0}
            excluded_domains = []
        else:
            raise ValueError("dataset name not found!")

        schema_path = os.path.join(data_path, "schema.json")
        schema = json.load(open(schema_path))

        for split in ["train", "dev", "test"]:
            print("--------Preprocessing {} set---------".format(split))
            out = open(os.path.join(data_bin_path, "{}.json".format(split)), "w")
            idx_out = open(os.path.join(data_bin_path, "{}.idx".format(split)), "w")
            dial_json = os.path.join(data_path, "{}.json".format(split))
            preprocess(dial_json, schema, out, idx_out, excluded_domains, frame_idxs, split)
            idx_out.close()
            out.close()

    print("--------Finish Preprocessing---------")


if __name__ == '__main__':
    main()
