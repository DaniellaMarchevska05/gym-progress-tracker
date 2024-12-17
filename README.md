
# Gym Progress Tracker

This application allows you to log your workout routines, track progress, and analyze your performance over time. It is built using Python with `Streamlit` for the frontend and `mysql-connector` for the backend database operations.

## Features

- **Log Workout**: Record your workout routines including date, exercises, sets, weights, and repetitions.
- **My Workouts**: View your logged workouts by date.
- **View Progress**: Analyze workout progress including exercise trends and total weight summary over time.

## Technologies Used

- **Python**: Streamlit for the user interface and `mysql-connector` for database management.
- **Database**: `GymProgressDB` database using MySQL with the following tables:
  - `Workout`: Stores workout sessions with `id` and `date`.
  - `Exercise`: Stores exercise names with `id` and `name`.
  - `SetRecord`: Links workouts with exercises, storing `weight`, `reps`, and foreign keys to `Workout` and `Exercise` tables.

## How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repository-url.git
   ```

2. **Set up the MySQL database**:
   - Create a new database named `GymProgressDB`.
   - Run the SQL scripts to create necessary tables (see below).

3. **Install dependencies**:
   ```bash
   pip install mysql-connector-python streamlit pandas matplotlib
   ```

4. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

## Database Setup

The following SQL commands are used to set up the database and tables:

```sql
CREATE DATABASE IF NOT EXISTS GymProgressDB;
USE GymProgressDB;

CREATE TABLE IF NOT EXISTS Workout (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS Exercise (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS SetRecord (  
    id INT AUTO_INCREMENT PRIMARY KEY,
    workout_id INT NOT NULL,
    exercise_id INT NOT NULL,
    weight FLOAT NOT NULL,
    reps INT NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES Workout(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES Exercise(id) ON DELETE CASCADE
);
```

## How It Works

1. **Database Initialization**: The `init_db()` function sets up the database and required tables (`Workout`, `Exercise`, `SetRecord`).
2. **Log Workout**: Use Streamlit interface to log workout sessions by selecting a date, exercise name, and recording sets with weights and repetitions.
3. **View Progress**: Analyze workout data over different periods (1 month, 6 months, 1 year). Select exercises to view trends and total weight summary.

### Streamlit Interface

The app consists of three main sections accessible via the sidebar menu:
- **Log Workout**: Log your workouts by entering a date and exercises. Record sets of weight and reps for each exercise.
- **My Workouts**: View your previous workouts by selecting a date and viewing details for each exercise.
- **View Progress**: Analyze workout data over selected periods. Plot exercise trends and total weight summary.

### Usage Examples

- **Log a Workout**:
  - Select the date for the workout.
  - Enter the exercise name.
  - Add sets by providing weight and repetitions.
  - Finish the exercise to complete the workout.

- **View Workout Progress**:
  - Select a date to view specific workout progress.
  - View sets, weights, and repetitions for each exercise logged on that date.

- **Analyze Progress**:
  - Choose analysis type (Exercise Trends, Weight Summary).
  - Select analysis period (1 Month, 6 Months, 1 Year).
  - View and plot the selected data.

## Contact

For any questions or feedback, please contact [your-email@example.com].

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.
