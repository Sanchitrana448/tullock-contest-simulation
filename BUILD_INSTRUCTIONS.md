Build & Run Instructions
=========================

1) Create and activate a Python virtual environment (Windows PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

(On CMD use `venv\Scripts\activate.bat`.)

2) Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Generate the dissertation draft:

```powershell
python notebooks/write_dissertation.py
```

Output: `results/dissertation_draft.docx` (and related figures are saved to `results/figures/` if matplotlib is installed).

Notes
-----
- If `python-docx` is missing, `notebooks/write_dissertation.py` will exit and print an instruction to install it.
- To enable plotting, install `matplotlib` and `seaborn` as needed.
