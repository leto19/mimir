def log_inputs(in_string, in_type):
    if in_type == "t":
        with open("data/logged_inputs/typed_inputs.txt","a") as f:
            f.writelines(in_string+"\n")
    elif in_type == "s":
        with open("data/logged_inputs/spoken_inputs.txt","a") as f:
            if in_string != "ERROR":
                f.writelines(in_string+"\n")
    else:
        print("invalid input type!")
