from flask import Flask, render_template, redirect, request, jsonify
import sqlite3

app = Flask(__name__)


# ----- Database Connection -----
def get_db_connection():
    """
    Establish and return a SQLite database connection with row factory enabled.
    """
    conn = sqlite3.connect('points.db')
    conn.row_factory = sqlite3.Row
    return conn


# ----- Database Initialization -----
def init_db():
    """
    Initialize the database with a table for team points and insert default teams.
    """
    conn = get_db_connection()
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS kids_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            points INTEGER DEFAULT 0
        )
        '''
    )
    conn.commit()

    # Default teams with emojis
    default_teams = [
        ("🦒 Ark Adventurers", 0),
        ("🔥 Fiery Furnace Friends", 0),
        ("🚗💨 Flaming Chariots", 0),
        ("🍞 Manna Munchers", 0),
        ("🏰 Jericho Jumpers", 0),
        ("🪨 Goliath Smashers", 0)
    ]

    for team in default_teams:
        conn.execute(
            'INSERT OR IGNORE INTO kids_points (name, points) VALUES (?, ?)',
            team
        )

    conn.commit()
    conn.close()


# ----- Public Leaderboard -----
@app.route('/')
def leaderboard():
    """
    Display the public leaderboard sorted by descending points.
    """
    conn = get_db_connection()
    teams = conn.execute(
        'SELECT * FROM kids_points ORDER BY points DESC'
    ).fetchall()
    conn.close()
    return render_template('leaderboard.html', teams=teams)


# ----- Admin Page -----
@app.route('/admin')
def admin():
    """
    Display the admin page for managing teams and points.
    """
    conn = get_db_connection()
    teams = conn.execute(
        'SELECT * FROM kids_points ORDER BY id'
    ).fetchall()
    conn.close()
    return render_template('admin.html', teams=teams)


@app.route('/add/<int:team_id>', methods=['POST'])
def add_points(team_id):
    """
    Add points to a specific team via admin form submission.
    """
    points = int(request.form.get('points', 1))
    conn = get_db_connection()
    conn.execute(
        'UPDATE kids_points SET points = points + ? WHERE id = ?',
        (points, team_id)
    )
    conn.commit()
    conn.close()
    return redirect('/admin')


@app.route('/add_team', methods=['POST'])
def add_team():
    """
    Add a new team to the leaderboard from admin page.
    """
    name = request.form['name']
    conn = get_db_connection()
    conn.execute(
        'INSERT OR IGNORE INTO kids_points (name, points) VALUES (?, 0)',
        (name,)
    )
    conn.commit()
    conn.close()
    return redirect('/admin')


@app.route('/clear_points', methods=['POST'])
def clear_points():
    """
    Reset all team points to zero.
    """
    conn = get_db_connection()
    conn.execute('UPDATE kids_points SET points = 0')
    conn.commit()
    conn.close()
    return redirect('/admin')


@app.route('/delete_team/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    """
    Delete a specific team from the leaderboard.
    """
    conn = get_db_connection()
    conn.execute('DELETE FROM kids_points WHERE id = ?', (team_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')


@app.route('/data')
def data():
    """
    Provide JSON data for chart rendering in the public leaderboard.
    """
    conn = get_db_connection()
    teams = conn.execute(
        'SELECT name, points FROM kids_points ORDER BY name'
    ).fetchall()
    conn.close()
    return jsonify({
        "labels": [t["name"] for t in teams],
        "points": [t["points"] for t in teams]
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
