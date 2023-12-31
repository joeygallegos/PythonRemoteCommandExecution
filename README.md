# PythonRemoteCommandExecution
This utility lets you execute preset commands to be run on the host by reading from a remote SQL database.

## How it works
I have set this up using a task setup in Task Scheduler to run on startup. It continuously loops and runs, waiting for a command to be dropped in the database.