from flask import Flask
import psycopg2

app = Flask(__name__)
connection = psycopg2.connect(
    host="postgres",
    port="5432",
    database="lat",
    user="admin",
    password="admin"
)
cursor = connection.cursor()

@app.route('/')
def get_student_data():
    cursor.execute('SELECT * FROM students LIMIT 1')
    student = cursor.fetchone()

    html_page = f"""
    <html>
    <head><title>Info</title></head>
    <body>
        <h1>Студент</h1>
        <p>ФИО: {student[1]}</p>
        <p>Шифр: {student[2]}</p>
    </body>
    </html>
    """

    return html_page

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)