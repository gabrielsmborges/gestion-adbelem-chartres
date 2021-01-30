from os import error
from sqlite3.dbapi2 import Cursor
from flask import Flask, render_template, request, redirect, session
import datetime
import sqlite3

app = Flask(__name__)


@app.route('/')
def hello_world():
    visitors=[]
    currentEvent = []
    count = 0
    try:
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            for visitor in cur.execute("SELECT * FROM visitors INNER JOIN events on events.id = visitors.eventId ORDER BY date DESC"):
                visitors.append({
                    "id": visitor[0],
                    "hour": datetime.datetime.strptime(visitor[2], '%Y-%m-%d %H:%M:%S.%f').strftime("%H:%M"),
                    "cargo": visitor[3],
                    "function": visitor[4],
                    "name": visitor[5],
                    "eventName": visitor[7]
                })
            for event in cur.execute("SELECT * FROM events WHERE enddate IS NULL ORDER BY begindate DESC"):
                #print(event)
                name = event[1],
                start = f"{datetime.datetime.strptime(event[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y à %H:%M')}"
                currentEvent.append({
                    "eventId": event[0],
                    "name": name,
                    "start" : start
                })
                if currentEvent:
                    currentEvent = currentEvent[0]
                    id = currentEvent['eventId']
                    print(id)
                    cur.execute(f"SELECT * FROM visitors WHERE eventId = {id}")
                    for row in cur:
                        count += 1

    except:
        pass
    return render_template('index.html', visitors=visitors, currentEvent = currentEvent, count = count)

@app.route('/create/event', methods = ['POST'])
def create_event():
    title = request.form.get('create-title')
    date = request.form.get('create-date')
    hour = request.form.get('create-hour')
    print(title, date, hour)
    parsedDate = f"{date} {hour}"
    parsedDate = datetime.datetime.strptime(parsedDate, '%Y-%m-%d %H:%M')
    id = ""
    try:
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            cur.execute('INSERT INTO events(title, begindate) VALUES(?,?)', (title, parsedDate))
            con.commit()
            for newEvent in cur.execute("SELECT id FROM events WHERE title = ? AND beginDate = ?", (title, parsedDate)):
                id = newEvent[0]
        return redirect(f'/manage/{id}')
    except:
        session['error'] = "Erreur de création d'évènement"
        return redirect('/')

@app.route('/manage')
def manage():
    data = []
    try:
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            for event in cur.execute("SELECT * FROM events ORDER BY begindate DESC"):
                data.append({
                    "id": event[0],
                    "title": event[1],
                    "date": event[2],
                    "end": event[3]
                })
    except:
        data = []
    print(data)
    return render_template('manage.html', data=data)

@app.route('/manage/<id>')
def see_event(id):
    data = []
    visitors = []
    with sqlite3.connect('gestion.db') as con:
        cur = con.cursor()
        for event in cur.execute("SELECT * FROM events WHERE id=?", (id)):
            date = f"{datetime.datetime.strptime(event[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y à %H:%M')}"
            end = event[3]
            if end:
                end = f"{datetime.datetime.strptime(event[3], '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y à %H:%M')}"
            data.append({
                "id": event[0],
                "title": event[1],
                "date": date,
                "end": end,
            })
        for visitor in cur.execute("SELECT * FROM visitors WHERE eventId=? ORDER BY date DESC", (id)):
            visitors.append({
                "id": visitor[0],
                "hour": datetime.datetime.strptime(visitor[2], '%Y-%m-%d %H:%M:%S.%f').strftime("%H:%M"),
                "cargo": visitor[3],
                "function": visitor[4],
                "name": visitor[5]
            })
    return render_template("event.html", data=data[0], visitors=visitors)

@app.route("/end/<id>")
def end_event(id):
    try:
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            cur.execute("UPDATE events SET enddate = ? WHERE id = ?;", (datetime.datetime.now(), id))
            con.commit()
    except:
        pass
    return redirect("/manage")

@app.route("/end/home/<id>")
def end_event_home(id):
    try:
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            cur.execute("UPDATE events SET enddate = ? WHERE id = ?;", (datetime.datetime.now(), id))
            con.commit()
    except:
        pass
    return redirect("/")

@app.route("/delete/<id>")
def delete_event(id):
    try:
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            cur.execute("DELETE FROM events WHERE id = ?", (id))
            cur.execute("DELETE FROM visitors WHERE eventId = ?", (id))
            con.commit()
    except:
        print("Exception")
        pass
    return redirect("/manage")



@app.route("/delete/visitor/<id>/<eventid>")
def delete_visitor(id, eventid):
    try:
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            cur.execute("DELETE FROM visitors WHERE id = ?", (id))
            con.commit()
    except:
        print("Exception")
        pass
    return redirect(f"/manage/{eventid}")


@app.route('/create/visitor', methods = ['POST'])
def create_visitor():
    try:
        name = request.form.get("visitor-name")
        funcao = request.form.get("visitor-funcao")
        cargo = request.form.get("visitor-cargo")
        id = request.form.get("id")
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            cur.execute('INSERT INTO visitors(eventId, date, cargo, function, name) VALUES(?, ?, ?, ?, ?)', (id, datetime.datetime.now(), cargo, funcao, name))
            con.commit()
        return redirect(f"/manage/{id}")
    except:
        return redirect("/manage")

@app.route("/manage/end/<id>")
def end_event_in_manage(id):
    try:
        with sqlite3.connect('gestion.db') as con:
            cur = con.cursor()
            cur.execute("UPDATE events SET enddate = ? WHERE id = ?;", (datetime.datetime.now(), id))
            con.commit()
    except:
        pass
    return redirect(f"/manage/{id}")


@app.route('/visitors')
def visitors():
    visitors = []
    with sqlite3.connect('gestion.db') as con:
        cur = con.cursor()
        for visitor in cur.execute("SELECT * FROM visitors INNER JOIN events on events.id = visitors.eventId ORDER BY date DESC"):
            print(visitor)
            visitors.append({
                "id": visitor[0],
                "hour": datetime.datetime.strptime(visitor[2], '%Y-%m-%d %H:%M:%S.%f').strftime("%H:%M"),
                "cargo": visitor[3],
                "function": visitor[4],
                "name": visitor[5],
                "eventName": visitor[7],
                "eventId": visitor[1]
            })
    return render_template('visitors.html', visitors=visitors)


if __name__ == "__main__":
    app.run(threaded=True, port=5000)