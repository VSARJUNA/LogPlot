import os
import time
import psutil
import tracemalloc
from MyDs import initialize as initialize_standard
from MyDsJ import initialize as initialize_json
from MyDsp import initialize as initialize_pandas

def profile_function(func, file_path):
    # Start profiling
    start_time = time.time()
    tracemalloc.start()
    initial_memory = psutil.Process(os.getpid()).memory_info().rss

    # Execute the function
    try:
        func(file_path)
        success = True
    except Exception as e:
        print(f"Error during function execution: {e}")
        success = False

    # End profiling
    final_memory = psutil.Process(os.getpid()).memory_info().rss
    elapsed_time = time.time() - start_time
    memory_usage = (final_memory - initial_memory) / (1024 * 1024)  # in MB
    tracemalloc.stop()

    # File size
    try:
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
    except Exception as e:
        print(f"Error getting file size: {e}")
        file_size = None

    # Collect stats
    return {
        'file_size': file_size,
        'elapsed_time': elapsed_time,
        'memory_usage': memory_usage,
        'success': success
    }

def profile_all_variants_across_files(file_paths):
    results = {}
    for file_path in file_paths:
        file_key = os.path.basename(file_path)
        results[file_key] = {}

        # Profile with MyDs.py
        print(f"\nProfiling standard MYDS (MyDs.py) with file: {file_path}")
        results[file_key]['MyDs'] = profile_function(initialize_standard, file_path)

        # Profile with MyDsJ.py
        print(f"\nProfiling JSON MYDS (MydsJ.py) with file: {file_path}")
        results[file_key]['MydsJ'] = profile_function(initialize_json, file_path)

        # Profile with MyDsp.py
        print(f"\nProfiling Pandas MYDS (MyDsp.py) with file: {file_path}")
        results[file_key]['MyDsp'] = profile_function(initialize_pandas, file_path)

    return results

# Files to profile
file_paths = [
    r"C:\Users\suhas\Documents\LogPilot\test.txt",
    r"C:\Users\suhas\Downloads\5G_PDSCH_sample_logs.txt",
    r"C:\Users\suhas\Downloads\blerone_1.txt"
]

# Get the profiling results
profiling_results = profile_all_variants_across_files(file_paths)

# Print out the profiling results
for file_name, variants in profiling_results.items():
    print(f"\nResults for {file_name}:")
    for variant, stats in variants.items():
        print(f"{variant} - File Size: {stats['file_size']:.3f} MB, Execution Time: {stats['elapsed_time']:.3f} s, Memory Usage: {stats['memory_usage']:.3f} MB, Success: {'Yes' if stats['success'] else 'No'}")
