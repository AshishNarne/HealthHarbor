# HealthHarbor
A collaborative WIP SWE project with the following functionality: Have a reminder/appointments website that can have both patient and doctor accounts that are connected. Doctors can schedule appointments and create reminders for their patients to take medicine.

## Important terminal commands

### To activate the venv
. .venv/bin/activate

### To run the project
python -m flask --app board run --port 8000 --debug

### To connect to the database in the command line
Starting from the root directory of the project

sqlite3 instance/db.sqlite

To show headers and align table columns
.header on
.mode table
