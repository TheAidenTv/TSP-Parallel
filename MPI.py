#######################################################################################
#   Program:    MPI.py
#   Authors:    Isaac Peacock, Aiden Timmons
#   Date:       April 10, 2024
#######################################################################################
#   Purpose:    Distributed Parallel implementation of the Traveling Salesman Problem
#               using MPI4py to spit the amount of permutations between processes
#######################################################################################
from mpi4py import MPI
import itertools
import math
import time
import folium

#############################################################
# Calculate the Euclidean distance between two given cites
#
# city1, city2: two cities to calculate the distance between
#############################################################
def calculate_distance(city1, city2):
    # Calculate Euclidean distance between two cities
    return math.sqrt((city1['x'] - city2['x'])**2 + (city1['y'] - city2['y'])**2)

##########################################################################
# Plot the path through the cities
#
# cities: list of cities to visit
# path: order of cities to visit
# fileName: name of the file to save the map (defaults to "TSP_Path.html")
##########################################################################
def plot_path(cities, path, fileName="TSP_Path.html"):
    x = [city['x'] for city in cities]
    y = [city['y'] for city in cities]

    # Create a map
    # Set the location to the average of all the cities
    # Folium is an external library used to plot path on a real map.
    m = folium.Map(location=[sum(y)/len(y), sum(x)/len(x)], tiles="Cartodb Positron", zoom_start=3)
    for i in range(len(path) - 1):
        # Draw a line between each city in the path
        folium.PolyLine([[cities[path[i]]['y'], cities[path[i]]['x']], [cities[path[i+1]]['y'], cities[path[i+1]]['x']]], color="blue", weight=2.5, opacity=1).add_to(m)
    # Draw a line from the last city to the first city
    folium.PolyLine([[cities[path[-1]]['y'], cities[path[-1]]['x']], [cities[path[0]]['y'], cities[path[0]]['x']]], color="blue", weight=2.5, opacity=1).add_to(m)

    for i in range(len(cities)):
        #show the city name on the map as a dot
        folium.CircleMarker([cities[i]['y'], cities[i]['x']], radius=2, color="black", fill=True, fill_color="black", fill_opacity=1).add_to(m)

    m.save(fileName)

#######################################################################
# Distributed Parallel implementation of the Traveling Salesman Problem
#
# cities: list of cities to visit
#######################################################################
def parallel_tsp(cities):
    startTime = time.time()
    num_cities = len(cities)

    # Divide the permutations among processes
    num_perms = math.factorial(num_cities)
    chunk_size = num_perms // size
    start_perm = rank * chunk_size
    end_perm = (rank + 1) * chunk_size if rank < size - 1 else num_perms

    min_distance = float('inf')
    best_path = None

    # Generate permutations for the current process
    # This uses pythons iter tools library (similar to Java's Iterable) to iterate through all possible
    # permutations and split it up based on a processors start_perm and end_perm indexes
    for perm in itertools.islice(itertools.permutations(range(num_cities)), start_perm, end_perm):

        distance = 0

        # Calculate the distance of travelling the path for this permutation
        for i in range(num_cities - 1):
            distance += calculate_distance(cities[perm[i]], cities[perm[i+1]])
        # Return to the starting city
        distance += calculate_distance(cities[perm[-1]], cities[perm[0]])

        # If this path is better than the processors current min, replace it
        if distance < min_distance:
            min_distance = distance
            best_path = perm
            # Was used for testing
            #print(f"Process {rank} found a better path: {min_distance}")

    # Gather all local results to process rank 0
    all_min_distances = comm.gather(min_distance, root=0)
    all_best_paths = comm.gather(best_path, root=0)

    endTime = time.time()

    if rank == 0:
        # Evaluate results from all processes
        min_distance = min(all_min_distances)
        best_path = all_best_paths[all_min_distances.index(min_distance)]



        #making a list of city names based on the best path
        optimal_path = [cities[i]["Name"] for i in best_path]

        # Print final result
        print("Minimum Distance:", min_distance)
        print("Best Path:", optimal_path)
        print("Execution Time:", endTime - startTime)

        # Plot the best path
        plot_path(cities, best_path)

if __name__ == "__main__":

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
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

    distance = 0
    # Starting path: [0, 1, 2, ..., N-1]
    start_path = list(range(len(cities)))
    # Plot the starting path
    plot_path(cities, start_path, "Original_Path.html")
    num_cities = len(cities)

    # Calculate the distance of the starting path to compare distance of best path
    for i in range(num_cities - 1):
        distance += calculate_distance(cities[i], cities[i+1])
    # Return to the starting city
    distance += calculate_distance(cities[-1], cities[0])
    
    if rank == 0:
        print("Starting Distance:", distance)

    # Run the parallel TSP algorithm
    parallel_tsp(cities)

###########################################################################################
# How to Run: mpiexec -n <num_processors> python MPI.py
# What we Ran: from 7 to 12 cities
# Where we Ran: On windows on Isaac's Laptop and On a Ubuntu VM on Aidens Laptop
# Number of Runs: We only got to run each a few times because of the time it takes to run
###########################################################################################
