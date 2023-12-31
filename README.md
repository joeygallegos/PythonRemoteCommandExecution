# PythonRemoteCommandExecution
This utility lets you execute preset commands to be run on the host by reading from a remote SQL database. I use this to remotely shutdown or reboot my machine. The Python script needs to be run from the computer that should pickup the commands.

## How it works
I have set this up using a task setup in Task Scheduler to run on startup. It continuously loops and runs, waiting for a command to be dropped in the database. When it finds a command dropped into the database, it checks which command it should run (based on the UUID). The UUID determines which pre-configured command should be run - reboot or shutdown.