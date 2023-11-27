from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import pymysql.cursors
from icecream import ic

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
app.config["SESSION_REFRESH_EACH_REQUEST"] = False

#Routing
@app.route('/')
def home():
    ic(session)
    return render_template('home/home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login(): #추가 해야하는 것들 1. 로그인 실패시 리로드
    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']
        ###############################
        connection = pymysql.connect(**DATABASE)
        try:
            with connection.cursor() as cur:
                #wrong_sql = "SELECT * FROM users WHERE id = '%s'" %(userID)
                #cur.execute(wrong_sql)
                sql = "SELECT * FROM users WHERE id = %s"
                cur.execute(sql, (userID,))
                result = cur.fetchone()
                print(result)

                if result and result['pwd'] == password:
                    session.permanent =True
                    app.permanent_session_lifetime = timedelta(hours=1)
                    session['user_id'] = userID
                    ic(session)
                    return redirect(url_for('home'))
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
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/signup', methods = ['GET', 'POST'])
def signup(): # 1. 있는 아이디 인가 검증 해야한다.
    if request.method == 'POST':
        userID = request.form['userID']
        username = request.form['username']
        password = request.form['password']
        checkPassword = request.form['checkPassword']
        email = request.form['email']

        if checkPassword != password:
            flash('Check the password value.')
            return redirect(url_for('signup'))

        connection = pymysql.connect(**DATABASE)
        try:
            with connection.cursor() as cur:
                sql = "select * from users WHERE id = %s"
                cur.execute(sql, (userID,))
                result = cur.fetchone()

                if result is not None:
                    return "User ID already exists", 400
                sql = "INSERT INTO users(id, pwd, email, username) VALUES (%s, %s, %s, %s)"
                cur.execute(sql, (userID, password, email, username))
            connection.commit()
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

    try:
        seq = int(seq)
    except(TypeError, ValueError):
        return "잘못된 게시글 번호입니다."

    connection = pymysql.connect(**DATABASE)
    result = None
    try:
        with connection.cursor() as cur:
            sql = "SELECT seq, title, author, content, date FROM board WHERE seq = %s"
            cur.execute(sql, (seq,))
            result = cur.fetchone()
            print(result)
    except:
        print('error')
    finally:
        connection.close()

    if result is None:
        return "해당하는 게시글이 없습니다."

    return render_template('board/post.html', title=result['title'], author=result['author'], content=result['content'], date=result['date'], seq = result['seq'])  # 새로운 템플릿에 게시글 정보 전달

@app.route('/board/cboard')
def create():
    return render_template('board/cboard.html')

@app.route('/board/submit_post', methods=['POST'])
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

@app.route('/board/edit_post/<int:seq>', methods=['GET', 'POST'])
def edit_post(seq):
    connection = pymysql.connect(**DATABASE)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        try:
            with connection.cursor() as cur:
                sql = "UPDATE board SET title = %s, content = %s WHERE seq = %s"
                cur.execute(sql, (title, content, seq))
            connection.commit()
        except:
            connection.rollback()
        finally:
            connection.close()
        return redirect(url_for('board'))
    else:
        result = None
        try:
            with connection.cursor() as cur:
                sql = "SELECT * FROM board WHERE seq = %s"
                cur.execute(sql, (seq,))
                result = cur.fetchone()
        except:
            connection.rollback()
        finally:
            connection.close()
        return render_template('board/edit_post.html', post=result)

@app.route('/board/delete/<int:seq>', methods=['GET', 'POST'])
def delete_post(seq):
    if request.method == 'POST':
        connection = pymysql.connect(**DATABASE)
        try:
            with connection.cursor() as cur:
                sql = "DELETE FROM board WHERE seq = %s"
                cur.execute(sql, (seq,))
            connection.commit()
        except:
            connection.rollback()
        finally:
            connection.close()
        return redirect(url_for('board'))

    return render_template('board/delete.html', seq=seq)



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