#######################################################################################
#   Program:    Sequential.py
#   Authors:    Isaac Peacock, Aiden Timmons
#   
#######################################################################################
#   Purpose:    Sequential implementation of the Traveling Salesman Problem
#               uses the itertools library to generate all permutations of the cities
#               and calculates the distance of each path to find the shortest path
#######################################################################################
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

#############################################################
# Brute force solution to the Traveling Salesman Problem
#
# cities: list of cities to visit
# start_path: starting path to begin the search
#############################################################
def tsp_bruteforce(cities, start_path):
    startTime = time.time()
    num_cities = len(cities)
    min_distance = float('inf')
    best_path = None

    # go through all permutations of the starting path
    for perm in itertools.permutations(start_path):
        distance = 0
        # Calculate the distance of the current permutation
        for i in range(num_cities - 1):
            distance += calculate_distance(cities[perm[i]], cities[perm[i+1]])
        # Return to the starting city
        distance += calculate_distance(cities[perm[-1]], cities[perm[0]])
        if distance < min_distance:
            min_distance = distance
            best_path = perm

    # Get the path as a list of city names
    optimal_path = [cities[start_path[i]]["Name"] for i in best_path]

    # Print final result
    print("Minimum Distance:", min_distance)
    print("Best Path:", optimal_path)
    print("Execution Time:", time.time() - startTime)

    # Plot the best path
    #plot_path(cities, best_path)

#######################################################################
# Plot the given path on a map
# and save it as an HTML file
#
# cities: list of cities to visit
# path: order of cities to visit
# fileName: name of the HTML file to save (defaults to "TSP_Path.html")
#######################################################################
def plot_path(cities, path, fileName="TSP_Path.html"):
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
        #show the city name on the map as a dot
        folium.CircleMarker([cities[i]['y'], cities[i]['x']], radius=2, color="black", fill=True, fill_color="black", fill_opacity=1).add_to(m)

    m.save(fileName)

if __name__ == "__main__":
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
        {"Name": 'Saskatoon', "x": -106.66, "y": 52.13}, #10
        {"Name": 'Yucon', "x": -136.26, "y": 64.32}, #11
        {"Name": 'Polar Bear Provincial Park', "x": -83.07, "y": 54.72}, #12
        #{"Name": 'Sept-Iles', "x": -66.38, "y": 50.20}, #13
        #{"Name": 'Yellowknife', "x": -114.38, "y": 62.45}
        ] #14

    # Starting path: [0, 1, 2, ..., N-1]
    start_path = list(range(len(cities)))
    x = [city['x'] for city in cities]
    y = [city['y'] for city in cities]

    tsp_bruteforce(cities, start_path)