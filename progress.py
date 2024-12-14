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


def make_connection_db():
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="new2025",
        database="GymProgressDB"
    )
    return connection


# Add workout to the database
def add_workout_to_db(date):
    connection = make_connection_db()
    c = connection.cursor()
    c.execute("INSERT INTO Workout (date) VALUES (%s)", (date,))
    connection.commit()
    workout_id = c.lastrowid
    c.close()
    connection.close()
    return workout_id


# Add exercise to the database
def add_exercise_to_db(name):
    connection = make_connection_db()
    c = connection.cursor()
    c.execute("INSERT INTO Exercise (name) VALUES (%s)", (name,))
    connection.commit()
    exercise_id = c.lastrowid
    c.close()
    connection.close()
    return exercise_id


# Add set to the database
def add_set_to_db(workout_id, exercise_id, weight, reps):
    connection = make_connection_db()
    c = connection.cursor()
    c.execute(
        "INSERT INTO SetRecord (workout_id, exercise_id, weight, reps) VALUES (%s, %s, %s, %s)",
        (workout_id, exercise_id, weight, reps)
    )
    connection.commit()
    c.close()
    connection.close()


# Get workout details by date
def get_workout_by_date(date):
    connection = make_connection_db()
    c = connection.cursor()
    c.execute(
        '''
        SELECT Exercise.name, SetRecord.weight, SetRecord.reps
        FROM Workout
        JOIN SetRecord ON Workout.id = SetRecord.workout_id
        JOIN Exercise ON SetRecord.exercise_id = Exercise.id
        WHERE Workout.date = %s
        ORDER BY Exercise.name, SetRecord.id
        ''', (date,)
    )
    results = c.fetchall()
    c.close()
    connection.close()
    return results


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
    if date and st.session_state.workout_id is None:
        st.session_state.workout_id = add_workout_to_db(date)

    exercise_name = st.text_input("Exercise Name", placeholder="Enter exercise name")

    if exercise_name:
        if "exercise_id" not in st.session_state:
            exercise_id = add_exercise_to_db(exercise_name)
            st.session_state.exercise_id = exercise_id

        st.subheader(f"Log Sets for '{exercise_name}'")

        # Inputs for weight and reps
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.5, value=0.0, key="weight_input")
        reps = st.number_input("Reps", min_value=1, step=1, value=1, key="reps_input")

        if st.button("Add Set"):
            new_set = {"weight": weight, "reps": reps}
            st.session_state.current_sets.append(new_set)
            add_set_to_db(st.session_state.workout_id, st.session_state.exercise_id, weight, reps)

        st.subheader("Current Sets")
        for i, set_data in enumerate(st.session_state.current_sets, start=1):
            st.write(f"Set {i}: {set_data['weight']} kg x {set_data['reps']} reps")

        # Finish Exercise Button
        if st.button("Finish Exercise"):
            if "exercise_id" in st.session_state:
                del st.session_state.exercise_id
            if "current_sets" in st.session_state:
                del st.session_state.current_sets
            st.success("Exercise finished!")

    else:
        st.info("Start logging by adding an exercise name.")

elif menu_option == "View Progress":
    st.subheader("View Progress")

    # Select Date
    selected_date = st.date_input("Select Date to View Progress", min_value=datetime(2000, 1, 1), max_value=datetime.now())

    if st.button("View Progress for Selected Date"):
        progress = get_workout_by_date(selected_date)
        if progress:
            st.write(f"Progress for {selected_date}:")
            current_exercise = None
            sets_by_exercise = {}

            for exercise_name, weight, reps in progress:
                if exercise_name not in sets_by_exercise:
                    sets_by_exercise[exercise_name] = []

                sets_by_exercise[exercise_name].append((weight, reps))

            for exercise_name, sets in sets_by_exercise.items():
                st.write(f"Exercise: {exercise_name}")
                for i, (weight, reps) in enumerate(sets, start=1):
                    st.write(f"  - Set {i}: {weight} kg x {reps} reps")

        else:
            st.warning("No progress found for the selected date.")
