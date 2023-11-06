from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import pymysql.cursors

#DB init
DATABASE = {
    'host' : 'localhost',
    'user' : 'root' ,   #비밀
    'password' : '9683',#비밀
    'db' : 'flask',
    'charset' : 'utf8',
    'cursorclass' : pymysql.cursors.DictCursor  #이 코드가 없으면 배열 형태로 리턴한다. 이 코드는 딕셔너리 형태로 리턴하게 만든다.
}

#APP init
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = "phantom" #비밀
app.permanent_session_lifetime = timedelta(hours= 1)

#Routing
@app.route('/')
def home():
    return render_template('home/home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']
        ###############################
        connection = pymysql.connect(**DATABASE)
        try:
            with connection.cursor() as cur:
                sql = "SELECT * FROM users WHERE id = %s"
                cur.execute(sql, (userID,))
                result = cur.fetchone()
                print(result)

                if result and result['pwd'] == password:
                    session.permanent =True
                    session['user_id'] = userID
                    print(session)
                    print("success")
                    return render_template('home/home.html')
                else:
                    print("false")
        except:
            connection.rollback()
            print('error')
        finally:
            connection.close()
        #####################################
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    # 로그아웃 처리: 세션에서 'user_id'와 'username' 제거
    session.pop('user_id', None)
    return redirect(url_for('home'))  # 홈페이지로 리다이렉션

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        userID = request.form['userID']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        ##############
        connection = pymysql.connect(**DATABASE)
        try:
            with connection.cursor() as cur:
                sql = "INSERT INTO users(id, pwd, email, username) VALUES (%s, %s, %s, %s)"
                cur.execute(sql,(userID, password,email, username))
            connection.commit()
            print(f"{userID}, {username}, {password}, {email}")
        except:
            connection.rollback()
            print('error')
        finally:
            connection.close()
        ##############
    return render_template('auth/signup.html')

@app.route('/board')
def board():
    connection = pymysql.connect(**DATABASE)
    result = []
    try:
        with connection.cursor() as cur:
            sql = "SELECT * FROM board"
            cur.execute(sql)
            result = cur.fetchall() #레코드를 배열형식
            print(result)
    except:
        connection.rollback()
        print('error')
    finally:
        connection.close()

    return render_template('board/board.html', posts=result)

@app.route('/board/post')
def post():
    seq = request.args.get('seq')  # URL의 GET 파라미터에서 seq 가져오기

    connection = pymysql.connect(**DATABASE)
    result = None
    try:
        with connection.cursor() as cur:
            sql = "SELECT title, author, content, date FROM board WHERE seq = %s"
            cur.execute(sql, (seq,))
            result = cur.fetchone()
            print(result)
    except:
        print('error')
    finally:
        connection.close()

    return render_template('board/post.html', title=result['title'], author=result['author'], content=result['content'], date=result['date'])  # 새로운 템플릿에 게시글 정보 전달

@app.route('/cboard')
def create():
    return render_template('board/cboard.html')

@app.route('/submit_post', methods=['POST'])
def submit_post():
    title = request.form['title']
    author = request.form['author']
    content = request.form['content']

    #########################
    connection = pymysql.connect(**DATABASE)
    try:
        with connection.cursor() as cur:
            sql = "INSERT INTO board(title, author, content) VALUES(%s, %s,%s)"
            cur.execute(sql, (title, author, content))
        connection.commit()
    except:
        connection.rollback()
        print('error')
    finally:
        connection.close()

    return redirect(url_for('board'))

@app.route('/community')
def community():
    if 'user_id' not in  session:
        flash('login first!!')
        return redirect(url_for('login'))

    connection = pymysql.connect(**DATABASE)
    messages = []
    try:
        with connection.cursor() as cur:
            sql = "SELECT * FROM message"
            cur.execute(sql)
            messages = cur.fetchall()
            print(messages)
    except:
        connection.rollback()
        print('error')
    finally:
        connection.close()
    return render_template('community/community.html', messages = messages)
@app.route('/send_message', methods=['POST'])
def send_message():
    author = request.form['author']
    content = request.form['message']

    connection = pymysql.connect(**DATABASE)

    try:
        with connection.cursor() as cur:
            sql = "INSERT INTO message(author, content) VALUES (%s, %s)"
            cur.execute(sql, (author, content))
            connection.commit()

    except:
        connection.rollback()
        print('error')
    finally:
        connection.close()
    #####################################
    return redirect(url_for('community'))


if __name__ == '__main__':
    app.run(debug=True)