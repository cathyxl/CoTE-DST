def get_predicted_slot_value(output_sent):
    if output_sent.lower().startswith("there is no answer"):
        return "NONE"
    return output_sent

