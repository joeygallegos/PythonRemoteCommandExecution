import schedule
import time
import os
import configparser
import mysql.connector
import subprocess


def setup_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)

    mysql_config = {
        "host": config.get("MYSQL", "HOST"),
        "port": config.getint("MYSQL", "PORT"),
        "user": config.get("MYSQL", "USER"),
        "password": config.get("MYSQL", "PASSWORD"),
        "database": config.get("MYSQL", "DATABASE_NAME"),
    }

    table_name = config.get("MYSQL", "DATABASE_TABLE")
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute(
        f"""
CREATE TABLE IF NOT EXISTS {table_name}
(
    id BIGINT(64) AUTO_INCREMENT PRIMARY KEY,
    source TEXT,
    command_uuid VARCHAR(36),
    used TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
                   """
    )
    conn.commit()
    return conn, cursor, table_name


# Local database of simple command names and their corresponding Windows CLI commands
COMMANDS_DICT = {
    "25c173df-952f-40e7-94a6-7f6ba77ea01e": 'shutdown /s /t 60 /c "PythonRemoteCommandExecutor: shutdown" /d U:5:19',
    "6e495198-17f1-455c-b44e-eb620c19fab1": 'shutdown /r /t 60 /c "PythonRemoteCommandExecutor: reboot" /d U:5:19',
}


# Define a function to check the MySQL server for commands and execute them
def check_and_execute_command():
    command_to_run = None
    print("Checking for commands")
    try:
        conn, cursor, table_name = setup_db()

        # Query for commands where "used" = 0
        cursor.execute(f"SELECT command_uuid FROM {table_name} WHERE used = 0 LIMIT 1;")
        commands = cursor.fetchall()

        for command in commands:
            # Execute the command (you can modify this part)
            # For example, print the command for demonstration purposes
            print("Executing command:", command[0])

            # Update the "used" flag to 1
            cursor.execute(
                f"UPDATE {table_name} SET used = 1, used_at = CURRENT_TIMESTAMP WHERE command_uuid = %s;",
                (command[0],),
            )
            conn.commit()

            # Look up the simple command in the local database
            command_to_run = COMMANDS_DICT.get(command[0])

            if command_to_run:
                print(f"Executing command: {command_to_run}")
            else:
                print(f"Command {command_to_run} not found in the local database.")

        cursor.close()
        conn.close()

        # If command to run present
        if command_to_run is not None:
            # Execute the command
            subprocess.run(command_to_run, shell=True)

    except Exception as e:
        print("Error:", str(e))


# Schedule the check_and_execute_commands function to run every minute
schedule.every(1).minutes.do(check_and_execute_command)

while True:
    schedule.run_pending()
    time.sleep(1)
