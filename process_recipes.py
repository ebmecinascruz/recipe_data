import subprocess
import os
from pathlib import Path
import time

def run_script(script_name: str, description: str) -> None:
    """
    Run a Python script and print its progress.
    
    Args:
        script_name: Name of the script to run
        description: Description of what the script does
    """
    print(f"\n=== {description} ===")
    print(f"Running {script_name}...")
    
    start_time = time.time()
    result = subprocess.run(["python", script_name], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Completed in {time.time() - start_time:.2f} seconds")
        print(result.stdout)
    else:
        print("Error occurred:")
        print(result.stderr)
        raise RuntimeError(f"Script {script_name} failed")

def main():
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Run the pipeline
    try:
        # Step 1: Scrape recipe data
        run_script(
            "scrape_recipe_data.py",
            "Scraping recipe data from Food.com"
        )
        
        # Step 2: Preprocess the data
        run_script(
            "preprocess_recipes.py",
            "Preprocessing recipe data"
        )
        
        # Step 3: Classify recipes
        run_script(
            "classify_recipes.py",
            "Classifying recipes by cuisine and difficulty"
        )
        
        print("\n=== Pipeline completed successfully! ===")
        print("Final output file: data/recipe_200_with_classification.csv")
        
    except Exception as e:
        print(f"\nError in pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main() 