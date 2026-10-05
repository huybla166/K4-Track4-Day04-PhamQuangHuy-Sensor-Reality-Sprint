import os
import webbrowser
import sys

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_file = os.path.join(repo_root, "DEMO_SIMULATOR.html")
    
    if not os.path.exists(html_file):
        print(f"Error: Could not find {html_file}")
        sys.exit(1)
        
    print(f"Launching ADAS Calibration Drift Interactive Simulator: {html_file}")
    webbrowser.open(f"file:///{os.path.abspath(html_file).replace(os.sep, '/')}")
    print("Demo opened in default web browser! Enjoy presenting!")

if __name__ == "__main__":
    main()
