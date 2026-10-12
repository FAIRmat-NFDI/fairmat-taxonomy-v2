# rep_modeller.py — GUI for the representation module

A modelling assistant: pick a taxonomy class, a representation type and its
components, see the Turtle, and check it with the HermiT reasoner.

## Requirements

| Need | Why |
|---|---|
| Python 3.9+ with `tkinter` | the GUI |
| `rdflib` | reading the ontology |
| Java (JRE) | runs HermiT |
| `owlready2` | provides `HermiT.jar` (or set `HERMIT_JAR=/path/to/HermiT.jar`) |

## Install

Linux (Ubuntu/Debian):

```bash
sudo apt install python3-venv python3-tk default-jre
python3 -m venv ~/rep-env
source ~/rep-env/bin/activate
pip install rdflib owlready2
```

Windows / macOS: tkinter comes with the standard Python installer; install Java,
then `pip install rdflib owlready2` (preferably in a virtual environment).

## Open a file

Pass `main.ttl` as an argument (it loads straight away):

```bash
source ~/rep-env/bin/activate
python gui_toolkit.py main.ttl
```

Or start without an argument and choose the file in the window:

```bash
python gui_toolkit.py
```

→ **Browse…** → select `main.ttl` → **Load**.

`main.ttl` must contain the representation module.