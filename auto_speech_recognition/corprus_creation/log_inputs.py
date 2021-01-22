def log_inputs(in_string, in_type):
    if in_type == "t":
        with open("../../data/typed_inputs.txt","a") as f:
            f.write(in_string)
    elif in_type == "s":
        with open("../../data/spoken_inputs.txt","a") as f:
            f.write(in_string)
    else:
        print("invalid input type!")
        