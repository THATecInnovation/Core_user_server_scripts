# Core_user_server_scripts

Scripts to create the required files for thaTEC:Core to implement a user server to distribute own programs via thaTEC:Core

## Requirements

Requires Python 3 for the execution of the script.
Tested with Python 3.10.5

## Usage

The user server / user directory must be a folder which contains a folder for each software module which should be distributed and updated using thaTEC:Core. The module name is given by the folder name and must not be identical to any module name available in the THATec Innovation device library!
Furthermore, the module folder must contain exactly 1 .exe file.

Place the *generate_Update.py* into the main folder and run the script. The script will search all folders for new and updated files and create additional required files within the module folders as well as a *Updates.csv* file in the main folder. Any found updates or deletions are printed to the terminal during the execution.

Subsequently, set the path to the user directory in thaTEC:Core and you are good to go and share your own software modules within thaTEC:Core.

In case of any issues, set the *verbose* option to *True* and check the output of the script.

## Contact
THATec Innovation GmbH
https://thatec-innovation.com/
contact@thatec-innovation.com