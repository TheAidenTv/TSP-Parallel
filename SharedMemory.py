#######################################################################################
#   Program:    SharedMemory.py
#   Authors:    Isaac Peacock, Aiden Timmons
#   Date:       April 10, 2024
#######################################################################################
#   Purpose:    Shared memory implementation of the Traveling Salesman Problem
#               using threading to spit the amount of permutations between processes.
#               Ran into issues since threading is not true parallelism.
#######################################################################################
import threading
import time
import math
import folium

# Dictionary of cities with their coordinates and names
cities = [
        {"Name": 'Saint John', "x": -66.07, "y": 45.27}, #1
        {"Name": 'Toronto', "x": -79.39, "y": 43.65}, #2
        {"Name": 'Vancouver', "x": -123.13, "y": 49.29}, #3
        {"Name": 'Motreal', "x": -73.54, "y": 45.52}, #4
        {"Name": "Saint John's", "x": -52.67, "y": 47.57}, #5
        {"Name": 'Fort McMurray', "x": -111.41, "y": 56.74}, #6
        {"Name": 'Iqaluit', "x": -68.52, "y": 63.75}, #7
        {"Name": 'PEI', "x": -63.38, "y": 46.39}, #8
        {"Name": 'Winnipeg', "x": -97.19, "y": 49.90}, #9
        #{"Name": 'Saskatoon', "x": -106.66, "y": 52.13}, #10
        #{"Name": 'Yucon', "x": -136.26, "y": 64.32}, #11
        #{"Name": 'Polar Bear Provincial Park', "x": -83.07, "y": 54.72}, #12
        #{"Name": 'Sept-Iles', "x": -66.38, "y": 50.20}, #13
        #{"Name": 'Yellowknife', "x": -114.38, "y": 62.45} #14
        ]

path = list(range(len(cities)))

##########################################################################
# Plot the path through the cities
#
# cities: list of cities to visit
# path: order of cities to visit
# fileName: name of the file to save the map (defaults to "TSP_Path.html")
##########################################################################
def plot_path(path, cities, filename="TSP_Path.html"):
    x = [city['x'] for city in cities]
    y = [city['y'] for city in cities]

    # Create a map
    # Set the location to the average of all the cities
    m = folium.Map(location=[sum(y)/len(y), sum(x)/len(x)], tiles="Cartodb Positron", zoom_start=3)
    for i in range(len(path) - 1):
        # Draw a line between each city in the path
        folium.PolyLine([[cities[path[i]]['y'], cities[path[i]]['x']], [cities[path[i+1]]['y'], cities[path[i+1]]['x']]], color="blue", weight=2.5, opacity=1).add_to(m)
    # Draw a line from the last city to the first city
    folium.PolyLine([[cities[path[-1]]['y'], cities[path[-1]]['x']], [cities[path[0]]['y'], cities[path[0]]['x']]], color="blue", weight=2.5, opacity=1).add_to(m)

    for i in range(len(cities)):
        #show the city on the map as a dot
        folium.CircleMarker([cities[i]['y'], cities[i]['x']], radius=2, color="black", fill=True, fill_color="black", fill_opacity=1).add_to(m)

    m.save()

#############################################################
# Calculate the Euclidean distance between two given cites
#
# city1, city2: two cities to calculate the distance between
#############################################################
def calculate_distance(city1, city2):
    # Calculate Euclidean distance between two cities
    return math.sqrt((city1['x'] - city2['x'])**2 + (city1['y'] - city2['y'])**2)

#############################################################
# Calculate the total distance of the path through the cities
#
# path: order of cities to visit
# cities: dictionary of cities to visit
#############################################################
def travel_distance(path, cities):
    distance = 0
    for i in range(len(path) - 1):
        distance += calculate_distance(cities[path[i]], cities[path[i+1]])
    distance += calculate_distance(cities[path[-1]], cities[path[0]])
    return distance

#############################################################
# Generator to get all permutations of the given path
# Function Was shown to us by Dr. Kim in CS 4795 (AI)
#
# path: list of cities to visit
#############################################################
def gen_perms(path):
    if len(path) <= 1:
        yield path
    else:
        for perm in gen_perms(path[1:]):
            for i in range(len(path)):
                yield perm[:i] + path[0:1] + perm[i:]

# Initialize the generator and global variables
gen = gen_perms(path)
min_dist = float('inf')
min_path = None

# Define a lock
lock = threading.Lock()

#############################################################
# Function for each thread to get the next permutation.
# Had to add a lock due to race conditions with generator
#############################################################
def get_next_perm():
    with lock:
        try:
            return next(gen)
        except StopIteration:
            return None

# Define number of threads
num_threads = 2
threads = []

########################################################
# Function to be executed by each thread.
# Calulates the distance for each permutation
# and updates the minimum distance and path if smaller
########################################################
def thread_function():
    global min_dist, min_path
    while True:
        perm = get_next_perm()
        if perm is None:
            break
        distance = travel_distance(perm, cities)
        # double if because if after the previous thread changed min_dist, have to again check if distance < min_dist
        if distance < min_dist:
            with lock:
                if distance < min_dist:
                    min_dist = distance
                    min_path = perm
            
# Create and start threads
start = time.time()
for i in range(num_threads):
    thread = threading.Thread(target=thread_function)
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Get the path as a list of city names
optimal_path = [cities[path[i]]["Name"] for i in min_path]
print(f"Time to run: {time.time() - start}")
print(f"Minimum distance: {min_dist}")
print(f"Best path: {optimal_path}")

#plot_path(min_path, cities)

###########################################################################################
# How to Run: python SharedMemory.py
# What we Ran: from 7 to 12 cities
# Where we Ran: On Windows on Isaac's Laptop and On an Ubuntu VM on Aidens Laptop
# Number of Runs: We only got to run this a few times because of the time it takes to run
###########################################################################################
