# HealthHarbor
A collaborative WIP SWE project with the following functionality: Have a reminder/appointments website that can have both patient and doctor accounts that are connected. Doctors can schedule appointments and create reminders for their patients to take medicine.

## Important terminal commands

### To create and activate a venv
Create
```
python -m venv venv
```

Activate

On Windows
```
.\venv\Scripts\activate
````

On MacOS/Linux
```
. .venv/bin/activate
```

### Install required packages
```
pip install -r requirements.txt
```

### To run the project
```
python -m flask --app src run --port 8000 --debug
```

### To connect to the database in the command line
Starting from the root directory of the project
```
sqlite3 instance/db.sqlite
```
To show headers and align table columns
```
.header on
.mode table
```
You will have to do this every time you open the database. To make it persistent, create ~/.sqliterc and paste those commands in it.
