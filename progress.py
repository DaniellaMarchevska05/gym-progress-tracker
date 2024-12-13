import mysql.connector
import streamlit as st
from datetime import datetime


# Database setup
def init_db():
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="new2025"
    )
    c = connection.cursor()
    c.execute("CREATE DATABASE IF NOT EXISTS GymProgressDB")
    c.execute("USE GymProgressDB")
    c.execute('''
        CREATE TABLE IF NOT EXISTS Workout (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL
        )
        ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Exercise (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
        ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS SetRecord (  
            id INT AUTO_INCREMENT PRIMARY KEY,
            workout_id INT NOT NULL,
            exercise_id INT NOT NULL,
            weight FLOAT NOT NULL,
            reps INT NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES Workout(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES Exercise(id) ON DELETE CASCADE
        )
        ''')
    connection.commit()
    c.close()
    connection.close()


# Add workout to the database
def add_workout_to_db(date):
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="new2025",
        database="GymProgressDB"
    )
    c = connection.cursor()
    c.execute("INSERT INTO Workout (date) VALUES (%s)", (date,))
    connection.commit()
    workout_id = c.lastrowid
    c.close()
    connection.close()
    return workout_id


# Add exercise to the database
def add_exercise_to_db(name):
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="new2025",
        database="GymProgressDB"
    )
    c = connection.cursor()
    c.execute("INSERT INTO Exercise (name) VALUES (%s)", (name,))
    connection.commit()
    exercise_id = c.lastrowid
    c.close()
    connection.close()
    return exercise_id


# Add set to the database
def add_set_to_db(workout_id, exercise_id, weight, reps):
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="new2025",
        database="GymProgressDB"
    )
    c = connection.cursor()
    c.execute(
        "INSERT INTO SetRecord (workout_id, exercise_id, weight, reps) VALUES (%s, %s, %s, %s)",
        (workout_id, exercise_id, weight, reps)
    )
    connection.commit()
    c.close()
    connection.close()


# Initialize database
init_db()

# Streamlit Interface
st.title("Gym Progress Tracker")
st.sidebar.title("Menu")
menu_option = st.sidebar.radio("Menu", ["Log Workout", "View Progress"])

if "current_sets" not in st.session_state:
    st.session_state.current_sets = []

if "workout_id" not in st.session_state:
    st.session_state.workout_id = None

if menu_option == "Log Workout":
    st.subheader("Log Your Workout")

    # Input: Workout Date
    date = st.date_input("Workout Date", min_value=datetime(2000, 1, 1), max_value=datetime.now())
    if st.button("Start Workout"):
        st.session_state.workout_id = add_workout_to_db(date)

    if st.session_state.workout_id:
        exercise_name = st.text_input("Exercise Name", placeholder="Enter exercise name")

        if exercise_name:
            if st.button("Add Exercise"):
                exercise_id = add_exercise_to_db(exercise_name)
                st.session_state.exercise_id = exercise_id
                st.session_state.current_sets = []
                st.success(f"Exercise '{exercise_name}' added!")

            if "exercise_id" in st.session_state:
                st.subheader(f"Log Sets for '{exercise_name}'")

                if "new_set" not in st.session_state:
                    st.session_state.new_set = {"weight": 0.0, "reps": 1}

                # Inputs for weight and reps
                weight = st.number_input(
                    "Weight (kg)", min_value=0.0, step=0.5, value=st.session_state.new_set["weight"], key="weight_input"
                )
                reps = st.number_input(
                    "Reps", min_value=1, step=1, value=st.session_state.new_set["reps"], key="reps_input"
                )

                if st.button("Add Set"):
                    st.session_state.current_sets.append({"weight": weight, "reps": reps})
                    add_set_to_db(st.session_state.workout_id, st.session_state.exercise_id, weight, reps)
                    st.success(f"Set added: {weight} kg x {reps} reps")

                    # Reset the fields for the next set
                    st.session_state.new_set = {"weight": 0.0, "reps": 1}

                if st.session_state.current_sets:
                    st.subheader("Current Sets")
                    for i, set_data in enumerate(st.session_state.current_sets, start=1):
                        st.write(f"Set {i}: {set_data['weight']} kg x {set_data['reps']} reps")

                # Finish Exercise Button
                if st.button("Finish Exercise"):
                    del st.session_state.exercise_id
                    st.session_state.current_sets = []
                    st.success("Exercise finished! Add a new exercise or finish the workout.")

    else:
        st.error("Start the workout session by selecting a date.")
