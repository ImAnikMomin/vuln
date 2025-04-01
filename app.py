from flask import Flask, request, render_template, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management


def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    
    #
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ('admin', 'admin123'),
            ('user', 'password'),
            ('john', 'johnpass'),
            ('alice', 'alice123'),
            ('bob', 'bobsecure')
        ]
        cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users)
    
    conn.commit()
    conn.close()

init_db()


@app.route("/", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Flaw in the code this must be fixed right now anything can be thought of as sql code
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print("[DEBUG] SQL Query:", query)  # For debugging

        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]  # Store username in session
            return redirect("/dashboard")  # Redirect to dashboard
        else:
            message = "Invalid credentials!"

    return render_template("login.html", message=message)


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")  # Redirect to login if not authenticated
    return render_template("dashboard.html", user=session["user"])


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
