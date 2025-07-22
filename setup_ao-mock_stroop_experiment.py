# This script collects the necessary dareplane modules to run a Stroop task together
# with the mockup version of the dp-ao-communication module
#
# The setup script is implemented in python, as python is required for the
# modules anyways, so for OS independence, this is not a bash script as it most
# naturally would be in the UNIX world.

import shutil
import sys
from pathlib import Path

import pip

# The name of the folder that is to be created to store all the modules
SETUP_FOLDER_NAME = "ao_mock_stroop"
BRANCH_NAME = SETUP_FOLDER_NAME  # used within each module

CONTROL_ROOM_URL = "git@github.com:bsdlab/dp-control-room.git"
AO_MOCKUP = "git@github.com:bsdlab/dp-ao-comm-mockup.git"
STROOP = "git@github.com:bsdlab/dp-stroop.git"
LSL_URL = "git@github.com:bsdlab/dp-lsl-recording.git"


def install_pip_package(package):
    if hasattr(pip, "main"):
        pip.main(["install", package])
    else:
        pip._internal.main(["install", package])


requ_modules = ["GitPython"]

for mod in requ_modules:
    try:
        __import__(mod)
    except ImportError:
        install_pip_package(mod)


# ----------------------------------------------------------------------------
# Grab the git repos
# ----------------------------------------------------------------------------
# from git import Repo
#
root_dir = Path(SETUP_FOLDER_NAME)
try:
    root_dir.mkdir(exist_ok=False)
except FileExistsError:
    print(f"Directory `{root_dir}` already exists. Exiting.")
    q = input("Do you want to overwrite it? [y/N] ")
    if q == "y":
        shutil.rmtree(root_dir)
        root_dir.mkdir()
    else:
        exit(1)


repos = []
print("Fetching dp-control-room")
repos.append(Repo.clone_from(CONTROL_ROOM_URL, root_dir / "dp-control-room"))

print("Fetching dp-ao-comm-mockup")
repos.append(Repo.clone_from(AO_MOCKUP, root_dir / "dp-ao-comm-mockup"))

print("Fetching dp-stroop")
repos.append(Repo.clone_from(STROOP, root_dir / "dp-stroop"))

print("Fetching dp-lsl-recording")
repos.append(Repo.clone_from(LSL_URL, root_dir / "dp-lsl-recording"))


# for each repo -> create a branch for the experiment
# Keep a branch for the local setup to separate local specific changes
# from general bugfixes and features (which would then be merged back to `main`)
for repo in repos:
    branch = repo.create_head(BRANCH_NAME)
    branch.checkout()

# ----------------------------------------------------------------------------
# Derived paths
# ----------------------------------------------------------------------------
# Data directory relative to SETUP_FOLDER_NAME
DATA_DIR = root_dir.joinpath("./data").resolve()

# ----------------------------------------------------------------------------
# Create configs
# ----------------------------------------------------------------------------

#
# >>> for dp-control-room
#
control_room_cfg = (
    """
[exe]

# -------------------- AO Mockup -----------------------------------------
[exe.modules.dp-ao-comm-mockup]                                      
    type = 'recording'
    port = 8081                                                                 
    ip = '127.0.0.1'
    path = '../dp-ao-comm-mock/build/ao_comm'

[exe.modules.dp-ao-comm-mockup.pcomms]                                      
# currently still manually defined. the module needs to define a get_pcomms in the future
STARTREC = ''
STOPREC = ''
STARTSTIM = '{"StimChannel": 10272, "FirstPhaseDelay_mS": 0, "FirstPhaseAmpl_mA": -0.5, "FirstPhaseWidth_mS": 0.06, "SecondPhaseDelay_mS": 0, "SecondPhaseAmpl_mA": 0.5, "SecondPhaseWidth_mS": 0.06, "Freq_hZ": 2, "Duration_sec": 2000, "ReturnChannel": 10273}'
STOPSTIM = '{"StimChannel": 10272}'
SETPATH = '{"Path": "c:\\Surgeries_Data\\VPtest\\"}'
SETSAVENAME = '{"fname": "block1_resting_OFF"}'
QUIT = ''

[python]
modules_root = '../'                                                            

# -------------------- LSL recording -----------------------------------------
[python.modules.dp-lsl-recording]                                      
    type = 'recording'
    port = 8082                                                                 
    ip = '127.0.0.1'

# -------------------- Stroop paradigm  ----------------------------------------
[python.modules.dp-stroop]                                     
    type = 'paradigm'
    port = 8084
    ip = '127.0.0.1'


[macros]
"""
    + f"""

[macros.run_modified]
    name = 'RUN MODIFIED STROOP'
    description = 'Run the modified stroop task'
[macros.run_modified.default_json]
    fname = 'sub-P001_ses-S001_run-001_task-modifiedstroop'
    data_root = '{DATA_DIR.resolve()}'
    block_nr = 1
    delay_s = 0.5                  # delay inbetween commands -> time for LSL recorder to respond
[macros.run_modified.cmds]
    # [<target_module>, <PCOMM>, <kwarg_name1 (optional)>, <kwarg_name2 (optional)>]
    com1 = ['dp-stroop', 'RUN MODIFIED STROOP', 'block_nr=block_nr']
    com2 = ['dp-ao-comm-mockup', 'SETSAVENAME', 'fname=fname']
    com3 = ['dp-ao-comm-mockup', 'STARTREC', 'fname=fname']
    com4 = ['dp-lsl-recording', 'SET_SAVE_PATH', 'fname=fname', 'data_root=data_root']
    com5 = ['dp-lsl-recording', 'UPDATE']
    com6 = ['dp-lsl-recording', 'SELECT_ALL']
    com7 = ['dp-lsl-recording', 'RECORD']

[macros.run_classical]
    name = 'RUN ClASSICAL STROOP'
    description = 'Run the classical stroop task'
[macros.run_classical.default_json]
    fname = 'sub-P001_ses-S001_run-001_task-classicalstroop'
    data_root = '{DATA_DIR.resolve()}'
    block_nr = 1
    delay_s = 0.5                  # delay inbetween commands -> time for LSL recorder to respond
[macros.run_classical.cmds]
    com1 = ['dp-lsl-recording', 'UPDATE']
    com2 = ['dp-lsl-recording', 'SELECT_ALL']
    com3 = ['dp-lsl-recording', 'SET_SAVE_PATH', 'fname=fname', 'data_root=data_root']
    com4 = ['dp-ao-comm-mockup', 'SETSAVENAME', 'fname=fname']
    com5 = ['dp-lsl-recording', 'RECORD']
    com6 = ['dp-ao-comm-mockup', 'STARTREC', 'fname=fname']
    com7 = ['dp-stroop', 'RUN CLASSICAL STROOP', 'block_nr=block_nr']

[macros.stop_recording]
    name = 'STOP RECORDING'
    description = 'stop the offline recording'
[macros.stop_recording.cmds]
    com1 = ['dp-lsl-recording', 'STOPRECORD']
    com2 = ['dp-ao-comm-mock', 'STOPREC']

[macros.stim]
    name = 'START STIMULATE'
    description = 'Start the stimulation'
[macros.stim.default_json]
    amplitude1_mA = 1
    amplitude2_mA = -1
    stim_channel = 10272
    ret_channel = 10273
    phase_width_mS = 0.06
    stim_freq_Hz = 130
    phase_delay_mS = 0
    duration_s = 2000
[macros.stim.cmds]
    # Important: the order or the kwargs needs to be exactly this!
    com1 = ['dp-ao-comm-mockup', 'STARTSTIM', 'StimChannel=stim_channel', 'FirstPhaseDelay_mS=phase_delay_mS', 'FirstPhaseAmpl_mA=amplitude1_mA', 'FirstPhaseWidth_mS=phase_width_mS', 'SecondPhaseDelay_mS=phase_delay_mS', 'SecondPhaseAmpl_mA=amplitude2_mA', 'SecondPhaseWidth_mS=phase_width_mS', 'Freq_hZ=stim_freq_Hz', 'RetChannel=ret_channel', 'Duration_sec=duration_s', 'ReturnChannel=ret_channel']

[macros.stop_stim]
    name = 'STOP STIMULATE'
    description = 'Start the stimulation'
[macros.stop_stim.default_json]
    stim_channel = 10272
[macros.stop_stim.cmds]
    com1 = ['dp-ao-comm-mock', 'STOPSTIM', 'StimChannel=stim_channel']
"""
)

control_room_cfg_pth = Path(
    f"./{SETUP_FOLDER_NAME}/dp-control_room/configs/ao_mockup_stroop.toml"
)
with open(control_room_cfg_pth, "w") as f:
    f.write(control_room_cfg)


# ----------------------------------------------------------------------------
# Create single run script in the control room
# ----------------------------------------------------------------------------
platform = sys.platform
suffix = ".ps1" if platform == "win32" else ".sh"

script_file = root_dir / "dp-control_room" / f"run_ao_mock_stroop_experiment{suffix}"

with open(script_file, "w") as f:
    f.write(
        f"""
        python -m control_room.main --setup_cfg_path="{control_room_cfg_pth.resolve()}"
        """
    )
