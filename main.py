from flask import Flask, render_template, request

app = Flask(__name__, static_url_path='', static_folder='static')

@app.route('/')
def home():
    return render_template('home/home.html')

@app.route('/login', methods = ['GET', ' POST'])
def login():
    if request.method == 'POST':
        pass
    return render_template('auth/login.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        userID = request.form['userID']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        print(f"{userID}, {username}, {password}, {email}\n 회원가입 완료")
    return render_template('auth/signup.html')

if __name__ == '__main__':
    app.run(debug=True)