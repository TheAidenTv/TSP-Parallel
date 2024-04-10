from mpi4py import MPI

# Initialize the MPI environment
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Print the rank and size (number of processes)
print(f"Hello from process {rank} of {size}")