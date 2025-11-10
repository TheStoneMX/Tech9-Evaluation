# Running with Conda Environment

## Quick Start with Conda

If you have a conda environment named `langgraph` with all dependencies installed:

```bash
# Navigate to implementation directory
cd 02_implementation

# Run the Streamlit app (auto-activates conda env)
./run_streamlit_conda.sh
```

That's it! The script will:
1. Activate the `langgraph` conda environment
2. Check for required dependencies
3. Open your browser to http://localhost:8501
4. Launch the Streamlit web interface

---

## Manual Conda Setup

If you need to create the `langgraph` conda environment:

```bash
# Create new conda environment
conda create -n langgraph python=3.9 -y

# Activate environment
conda activate langgraph

# Install dependencies
pip install -r requirements.txt
```

---

## Verify Your Environment

Check if the `langgraph` environment exists:

```bash
conda env list
```

You should see `langgraph` in the list.

---

## Environment Activation

The `run_streamlit_conda.sh` script automatically activates the conda environment.

If you want to run commands manually:

```bash
# Activate conda environment
conda activate langgraph

# Run Streamlit
streamlit run streamlit_app.py

# Or run the main script
python main.py
```

---

## Troubleshooting

### Environment Not Found

```bash
# Error: Could not find conda environment: langgraph

# Solution: Create the environment
conda create -n langgraph python=3.9 -y
conda activate langgraph
pip install -r requirements.txt
```

### Dependencies Missing

```bash
# If you get import errors after activating the environment:

conda activate langgraph
pip install -r requirements.txt
```

### Streamlit Not Installed

```bash
conda activate langgraph
pip install streamlit
```

---

## Using VSCode with Conda

1. Open Command Palette (`Cmd+Shift+P`)
2. Type "Python: Select Interpreter"
3. Choose the `langgraph` conda environment
4. Terminal will automatically activate the environment

---

## Alternative: Create New Environment

If you want to create a fresh environment for this project:

```bash
# Create environment with specific name
conda create -n research_assistant python=3.9 -y

# Activate
conda activate research_assistant

# Install dependencies
cd 02_implementation
pip install -r requirements.txt

# Update the script to use new environment name
# Edit run_streamlit_conda.sh and change:
# conda activate langgraph
# to:
# conda activate research_assistant
```

---

## Benefits of Conda Environment

✅ Isolated dependencies (no conflicts with other projects)
✅ Consistent Python version across team
✅ Easy to recreate on different machines
✅ Better package management for data science libraries

---

## Exporting Your Environment

To share your exact environment with others:

```bash
# Activate environment
conda activate langgraph

# Export to file
conda env export > environment.yml

# Others can recreate with:
# conda env create -f environment.yml
```

---

## Quick Reference

```bash
# Create environment
conda create -n langgraph python=3.9

# Activate environment
conda activate langgraph

# Install dependencies
pip install -r requirements.txt

# Run Streamlit (auto-activates)
./run_streamlit_conda.sh

# Or manually
streamlit run streamlit_app.py

# Deactivate when done
conda deactivate
```
