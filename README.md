# AO Mockup Stroop example

This setup script provides you with a Dareplane setup containing:

- the [`dp-ao-comm-mockup`](https://github.com/bsdlab/dp-ao-comm-mockup) module - to simulate the communication with the [NeuroOmega's](https://www.alphaomega-eng.com/Neuro-Omega-System) API, usually done with the [`dp-ao-communication`](https://github.com/bsdlab/dp-ao-communication) module.
- the [`dp-stroop`](https://github.com/bsdlab/dp-stroop) to run a the modified or classical Stroop task.
- the [`dp-control-room`](https://github.com/bsdlab/dp-control-room) to provide a GUI for running the experiments.

## Installation

### Python venv

Create a python environment and install the dependencies as of the `requirements.txt` file.

E.g. using [`uv`](https://docs.astral.sh/uv/guides/install-python/):

```
uv venv myvenv
```

Activate the environment:
On UNIX

```
source .myvenv/bin/activate
```

On Windows

```
.myvenv/Scripts/activate
```

Install the dependencies:

```
uv pip install -r requirements.txt
```
