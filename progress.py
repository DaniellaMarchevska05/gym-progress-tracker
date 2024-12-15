import mysql.connector
import streamlit as st
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


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

def get_progress_data():
    connection = make_connection_db()
    c = connection.cursor()
    c.execute(
        '''
        SELECT Workout.date, Exercise.name, SetRecord.weight, SetRecord.reps
        FROM Workout
        JOIN SetRecord ON Workout.id = SetRecord.workout_id
        JOIN Exercise ON SetRecord.exercise_id = Exercise.id
        ORDER BY Workout.date
        '''
    )
    results = c.fetchall()
    c.close()
    connection.close()
    return results

def get_total_weight_summary(df):
    df["TotalWeight"] = df["Weight"] * df["Reps"]  # Calculate total weight for each set
    return df.groupby(pd.Grouper(key="Date", freq="M"))["TotalWeight"].sum().reset_index()

# Initialize database
init_db()

# Streamlit Interface
st.title("Gym Progress Tracker")
st.sidebar.title("Menu")
menu_option = st.sidebar.radio("Choose one of the options", ["Log Workout", "My Workouts", "View Progress"])

if "current_sets" not in st.session_state:
    st.session_state.current_sets = []

if "workout_id" not in st.session_state:
    st.session_state.workout_id = None

if menu_option == "Log Workout":
    st.subheader("Log Your Workout")

    # Input: Workout Date
    if "workout_date" not in st.session_state:
        st.session_state.workout_date = datetime.now().date()

    date = st.date_input("Workout Date", value=None, min_value=datetime(2000, 1, 1), max_value=datetime.now())

    if not date:
        st.warning("Select the date before logging your workout")
    elif st.session_state.workout_id is None:
        date_str = date.strftime("%Y-%m-%d")  # Ensure proper format
        st.session_state.workout_id = add_workout_to_db(date_str)
        st.success(f"Workout logged for {date_str}")


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
        if not st.session_state.current_sets:  # Check if no sets have been added
            st.warning("Add at least one set to the current exercise before finishing it.")
        else:
            st.session_state.workout_date = date  # Update the date stored in session state
            if "exercise_id" in st.session_state:
                del st.session_state.exercise_id
            if "current_sets" in st.session_state:
                del st.session_state.current_sets
            st.session_state.workout_id = None  # Clear workout_id to log a new workout
            st.success("Exercise finished!")



elif menu_option == "My Workouts":
    st.subheader("My Workouts")

    # Select Date
    selected_date = st.date_input("Select Date to View Your Workout", min_value=datetime(2000, 1, 1), max_value=datetime.now())

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

elif menu_option == "View Progress":
    st.subheader("Analyze Your Workout Progress")

    # Fetch data
    progress_data = get_progress_data()
    if progress_data:
        # Convert data to a DataFrame
        df = pd.DataFrame(progress_data, columns=["Date", "Exercise", "Weight", "Reps"])
        df["Date"] = pd.to_datetime(df["Date"])

        # Choose analysis type
        analysis_type = st.radio("Choose analysis type", ["Exercise Trends", "Weight Summary"])

        # Select analysis period
        analysis_period = st.radio("Select analysis period", ["1 Month", "6 Months", "1 Year"])

        # Filter data based on period
        today = datetime.now()
        if analysis_period == "1 Month":
            start_date = today - pd.DateOffset(months=1)
        elif analysis_period == "6 Months":
            start_date = today - pd.DateOffset(months=6)
        elif analysis_period == "1 Year":
            start_date = today - pd.DateOffset(years=1)

        filtered_df = df[df["Date"] >= start_date]

