What you will set up and why it matters for PyMart
You will set up a clean, repeatable way to run PyMart by isolating its Python dependencies from everything else on your machine. The core idea is simple: PyMart should behave the same for every teammate, on every laptop, and in every run. That only happens when the project’s packages and versions are controlled, verified, and easy to reproduce.
First, you will create an isolated Python environment so PyMart’s libraries do not conflict with other projects or global installs. Next, you will use PIP to install the exact third party packages PyMart needs, confirm what is installed, and capture that state so it can be recreated later. Your primary workflow will be VS Code plus a terminal. You will edit files in the editor, then run short commands to install, inspect, and reproduce dependencies without guesswork.

[An image about the PyMart dependency workflow from venv creation to reproducible installs]

Prepare the PyMart workspace in VS Code
Open VS Code, then use File → Open Folder… to open the root PyMart project folder (the one that contains your main project files). Confirm you are working inside that folder by checking the Explorer tree on the left and running pwd (macOS/Linux) or cd (Windows) in the integrated terminal to see the current path. If the terminal shell is not the one you expect, open the Command Palette and choose Terminal: Select Default Profile, then create a new terminal so the profile is applied.
Next, verify the Python interpreter VS Code will use for PyMart. In the status bar, select the Python version (or open the Command Palette and choose Python: Select Interpreter) and pick the intended interpreter for this project. If you do not choose deliberately, VS Code may use a global Python or a different environment, which can make later installs appear to “not work” even though they installed somewhere else.
Decide where the virtual environment folder will live before you create it. A common, convenient choice is a local folder inside the project (often named .venv) so the environment stays tied to PyMart and is easy to select. If your organization prefers keeping environments outside the repo (for example, in a centralized directory), use that standard instead. What matters most is consistency and making sure VS Code points to that environment once it exists.
Create and activate a virtual environment for PyMart
Create an isolated Python environment inside the PyMart project so packages you install for PyMart do not affect other projects or your system Python. From the PyMart project root (the folder that contains your code), create the environment in a local folder named .venv so it stays clearly tied to this project.
Create the venv:

python -m venv .venv
Activate it and confirm your terminal prompt changes to show the environment name:

macOS/Linux (bash/zsh):

source .venv/bin/activate
Windows (PowerShell):

.\.venv\Scripts\Activate.ps1
After activation, validate that python and pip resolve to the venv executables (not the system ones):

macOS/Linux:

which python
which pip
python -m pip --version
Windows (PowerShell):

Get-Command python
Get-Command pip
python -m pip --version
The paths should point inside .venv (for example, .venv/bin/... or .venv\Scripts\...). When you are done working, deactivate with:

deactivate
Install PyMart third party packages with PIP
With your PyMart virtual environment activated, install third-party packages using PIP so they land in the environment’s own site-packages (not your system Python). A good starter pair for a small retail or inventory workflow is requests for calling supplier or pricing APIs, and tabulate for printing clean, readable tables for stock counts, reorder lists, or end-of-day summaries.
Run these installs from the same terminal where the environment is active:

python -m pip install requests tabulate

Watch for a successful completion message and no error tracebacks.

If you have multiple Pythons installed, prefer python -m pip ... over pip ... so the install is tied to the currently active interpreter.

requests matters when PyMart needs to fetch external data (for example, pulling item details by SKU from a vendor endpoint). tabulate matters when PyMart staff need quick, readable console output (for example, a neatly formatted “low stock” report) without building a full UI.

Verify installation using pip list and pip show
After installing PyMart’s third-party dependencies, verify what actually landed in your environment. Start by listing packages so you can spot the newly installed dependencies and confirm they are present in the active setup.
Run:

pip list
Locate the packages you just installed (for example, requests, pandas, numpy, or whatever PyMart requires). If you do not see them, pause and confirm you installed into the same environment you are currently using.

Next, inspect a specific package to confirm its version and where it was installed:

pip show <package-name>
Pay attention to:

Version: matches what you intended to install

Location: the folder where the package is installed

Cross-check that the Location points inside the active virtual environment. A quick sanity check is to compare it to your venv path (commonly a .venv/ directory in your project). If pip show reports a location outside your venv (for example, a global Python site-packages directory), you are not installing into the environment you think you are, and you should re-activate the venv and repeat the install.
Freeze dependencies into a reproducible requirements file
Once PyMart runs correctly in your virtual environment, capture that exact set of installed packages in a file that another person (or a CI job) can recreate later. This is what makes your setup repeatable across machines and prevents “it works on my laptop” drift.
From the activated virtual environment, generate and place the file at the project root:

Run pip freeze > requirements.txt

Open requirements.txt and review it. Confirm it lists the packages you intentionally installed (and their pinned versions), for example requests==2.32.3

Save it in the repository root (next to files like README.md or pyproject content, if present) so onboarding starts with a single, obvious install command

Simulate a fresh setup and reinstall from requirements
To mimic a clean machine, exit your current virtual environment first, then recreate everything from scratch. Deactivate the current environment, then remove the old environment folder if you are keeping it in-project (for example, delete .venv/). This step is what makes the test meaningful. If you keep using an existing environment, you are not proving your requirements.txt can rebuild PyMart reliably.
Create a brand-new environment and activate it, then reinstall exactly what was frozen:

Create a new environment (for example: python -m venv .venv)

Activate it (Windows: .venv\Scripts\activate. macOS/Linux: source .venv/bin/activate)

Install from the file: pip install -r requirements.txt

Verify consistency by comparing pip list to what you expect, or by running pip freeze and confirming it matches your requirements.txt (aside from small ordering differences).

Uninstall a package and confirm removal
Choose one of the third-party packages you installed earlier (for example, requests) and remove it from the active virtual environment:

python -m pip uninstall requests
When prompted, confirm with y. This removes the package files from your environment’s site-packages, but it does not automatically update any requirements.txt you already generated.

Verify the removal in two different ways. First, confirm it no longer appears in the environment’s package list:

python -m pip list | findstr requests    # Windows
# or
python -m pip list | grep requests       # macOS/Linux
Then confirm pip can’t display its metadata anymore:

python -m pip show requests
pip show should return a warning like “Package(s) not found.” If it still shows details, you likely uninstalled from a different Python environment than the one your project is using. Re-check that your virtual environment is activated and re-run the commands.

If you are maintaining a reproducible setup, regenerate your requirements file after the change so future installs match what’s currently in the environment:

python -m pip freeze > requirements.txt
[An image about uninstall flow showing package removal from site-packages and verification checks]

Concrete outcome
You now have a PyMart setup that is both usable day to day and repeatable from scratch. Your environment is isolated, your dependencies are recorded, and your install lifecycle is proven end to end inside VS Code.

By the end of this lab, you should be able to point to these concrete deliverables:

A working PyMart virtual environment created and verified in VS Code.

A reproducible requirements.txt that can rebuild dependencies from scratch.

A validated workflow for installing, freezing, reinstalling, and uninstalling packages.