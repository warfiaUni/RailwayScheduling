# RailwayScheduling

Attempt at solving the [Flatland Challenge](https://flatland.aicrowd.com/intro.html) with ASP.

1. [Getting Started](#getting-started)
   1. [Prerequisites](#prerequisites)
   1. [Installation](#installation)
1. [How to use](#how-to-use)
1. [Fact Format for Instance Generation](#fact-format-for-instance-generation)
1. [Links](#links)

## Getting Started

### Prerequisites

The only prerequisite for this project is [Python](https://www.python.org/). It is currently recommended to use **Python 3.10** in order to avoid conflicts with Flatland.

### Installation

1. Clone this repository

   ```sh
   git clone https://github.com/warfiaUni/RailwayScheduling.git
   ```

2. Create a new python virtual environment (or use an existing one)

   ```sh
   py -m venv my_new_python_environment
   ```

3. Activate the virtual environment
   <details>
   <summary>Windows</summary>

   cmd.exe

   ```sh
   source my_new_python_environment/Scripts/activate.bat
   ```

   PowerShell

   ```sh
   source my_new_python_environment/Scripts/activate.ps1
   ```

   </details>
   <details>
   <summary>Linux</summary>

   (depending on distribution):

   bash

   ```sh
   source my_new_python_environment/bin/activate
   ```

4. Go into cloned repository directory
5. Install the project as an editable package

   ```sh
   pip install -e .
   ```

The project is now ready to be used in any project using the python virtual environment.

[back to top](#railwayscheduling)

## How to use

1. Check whether the project is installed correctly by typing

   ```
   rasch
   ```

   If successful this should start the application with the default parameters specified in `config.py`.

2. Continue by using

   ```
   rasch <encoding_name> <environment_name>
   ```

   This runs the program with `<encoding_name>.lp` and `<environment_name>.pkl`.
    <details>
    <summary>Example</summary>

   ```
   rasch base simple_switch_map
   ```

   This tries to run the program with `base.lp` as an encoding and `simple_switch_map.pkl` as environment.
    </details>

[back to top](#railwayscheduling)

## Links

Useful links for more information on Flatland and Clingo

- Flatland
  - Official Flatland website: https://www.flatland-association.org/
  - Flatland on pypi: https://pypi.org/project/flatland-rl/
  - Flatland on github: https://github.com/flatland-association/flatland-rl
- Clingo
  - Clingo: https://potassco.org/clingo/
  - Potassco Guide on github: https://github.com/potassco/guide/releases/

[back to top](#railwayscheduling)
