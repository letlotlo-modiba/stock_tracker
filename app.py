"""
Root entrypoint for Streamlit Stock Portfolio Dashboard.
Allows running: streamlit run app.py (or streamlit run dashboard/app.py)
"""
import os
import sys

# Ensure dashboard directory is in path and run the dashboard app
dashboard_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard")
app_path = os.path.join(dashboard_dir, "app.py")

if __name__ == "__main__":
    import runpy
    runpy.run_path(app_path, run_name="__main__")
else:
    # When executed via `streamlit run app.py`, Streamlit imports or execs the file
    with open(app_path, "r", encoding="utf-8") as f:
        code = compile(f.read(), app_path, "exec")
        exec(code, globals())
