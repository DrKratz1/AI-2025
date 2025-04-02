import random 
import os 
import csv 

#
# REMEMEBER THE SEEDS
#

# python -m search.test_case_generator

RANDOM_SEED = 967120123

random.seed(RANDOM_SEED)

# Generate the Positions for Blue Frogs
def generate_blue_frogs(exclude_value):

    sample_size=6
    lower=1
    upper=64

    while True:
        # Generate 6 unique random numbers
        random_numbers = random.sample(range(lower, upper + 1), sample_size)
        
        # Resample if the excluded value is in the sample
        if exclude_value not in random_numbers:
            return random_numbers


# can change the probabilities to make it easier / harder for the algorithm... ss
def test_case_generator():

    red_sym = "r"
    blue_sym = 'b'
    lily_sym = "*"

    # append to the list... 
    map_list = [" "] * 64

    # probabilties... 
    prob_lily = 30

    # need to make sure that one red frog is placed on the first file (random generate between positions 1 and 8) 
    # (this is a to be placed there) 
    rand_red = random.randint(0, 7)
    map_list[rand_red] = red_sym

    # Allocate the blue frogs... 
    blue_frog_pos = generate_blue_frogs(rand_red)

    for blue_frog in blue_frog_pos:
        map_list[blue_frog] = blue_sym

    for position in range(len(map_list)):

        # Check to see whether its a red frog... 
        if map_list[position] == " ": 

            # generator to determine whether a lilypad is added to the file... 
            rand_int = random.randint(1, 64)
        
            # Check for Lily pad positions... 
            if rand_int <= prob_lily:
                map_list[position] = lily_sym   
        else: 
            continue

    return map_list

def csv_case_writer(csv_input):
    
    map = ""
    counter = 0

    # convert to string first... 
    for input in csv_input:

        if counter == 7:
            map = map + input + '\n'
            counter = 0
            continue

        else: 
            map = map + input + ','
            counter += 1
    
    # Define the CSV file path
    output_folder = os.path.join('.', 'test-vis_random.csv')

    # Write the string to a CSV file
    with open(output_folder, mode='w') as file:
        file.write(map)

    return map

test_map = test_case_generator()
map_test = csv_case_writer(test_map)

