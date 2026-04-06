from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import requests
from flask import Flask, render_template, request, jsonify
import bcrypt
import random
import string
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
import os
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/loan_docs'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs('static/uploads/loan_docs', exist_ok=True)

db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    aadhaar = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    from_account = db.Column(db.String(20), nullable=False)
    to_account = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())



class CreditCard(db.Model):
    __tablename__ = 'credit_cards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_number = db.Column(db.String(20), unique=True, nullable=False)
    credit_limit = db.Column(db.Float, nullable=False)
    outstanding_balance = db.Column(db.Float, default=0.0)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    experience = db.Column(db.String(20), nullable=False)
    cover_letter = db.Column(db.Text)
    resume_path = db.Column(db.String(200))
   
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
class SchemeApplication(db.Model):
    __tablename__ = 'scheme_applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheme_name = db.Column(db.String(100), nullable=False)
    scheme_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
class InterestRate(db.Model):
    __tablename__ = 'interest_rates'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    min_rate = db.Column(db.Float, nullable=False)
    max_rate = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())    
class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tenure = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    income_proof = db.Column(db.String(200))
    id_proof = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())    
class NriEnquiry(db.Model):
    __tablename__ = 'nri_enquiries'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())    
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/check-login')
def check_login():
    return jsonify({'logged_in': 'user_id' in session})
@app.route('/apply-scheme', methods=['POST'])
def apply_scheme():
    if 'user_id' not in session:
        return jsonify({'success': False, 'redirect': '/login'})
    
    data = request.get_json()
    scheme_name = data.get('scheme_name')
    scheme_type = data.get('scheme_type')

    existing = SchemeApplication.query.filter_by(
        user_id=session['user_id'],
        scheme_name=scheme_name
    ).first()

    if existing:
        return jsonify({'success': False, 'message': 'You have already applied for this scheme.'})

    application = SchemeApplication(
        user_id=session['user_id'],
        scheme_name=scheme_name,
        scheme_type=scheme_type
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Successfully applied for {scheme_name}. Our team will contact you within 2 working days.'})
@app.route('/currency-rates')
def currency_rates():
    try:
        response = requests.get(
            'https://api.frankfurter.app/latest?from=USD&to=INR,EUR,GBP,JPY,SGD',
            headers={'Cache-Control': 'no-cache'}
        )
        data = response.json()
        rates = data['rates']
        return jsonify({
            'rates': {
                'USD': rates['INR'],
                'EUR': round(rates['INR'] / rates['EUR'], 2),
                'GBP': round(rates['INR'] / rates['GBP'], 2),
                'SGD': round(rates['INR'] / rates['SGD'], 2),
                'JPY': round(rates['INR'] / rates['JPY'], 2),
            },
            'status': 'success',
            'date': data['date']
        })
    except Exception as e:
        return jsonify({
            'rates': {
                'USD': 93.25,
                'EUR': 101.50,
                'GBP': 120.30,
                'SGD': 72.10,
                'JPY': 0.62,
            },
            'status': 'fallback',
            'date': 'N/A'
        })
@app.route('/market-data')
def market_data():
    try:
        gold_response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        gold_data = gold_response.json()
        usd_inr = gold_data['rates']['INR']
        return jsonify({
            'status': 'success',
            'data': [
                {'name': 'SENSEX', 'value': '73,452.32', 'change': '+245.67', 'up': True},
                {'name': 'NIFTY 50', 'value': '22,326.90', 'change': '+78.45', 'up': True},
                {'name': 'GOLD/10g', 'value': '₹71,450', 'change': '+320', 'up': True},
                {'name': 'USD/INR', 'value': f'₹{round(usd_inr, 2)}', 'change': '+0.12', 'up': True},
            ]
        })
    except:
        return jsonify({
            'status': 'error',
            'data': [
                {'name': 'SENSEX', 'value': '73,452.32', 'change': '+245.67', 'up': True},
                {'name': 'NIFTY 50', 'value': '22,326.90', 'change': '+78.45', 'up': True},
                {'name': 'GOLD/10g', 'value': '₹71,450', 'change': '+320', 'up': True},
                {'name': 'USD/INR', 'value': '₹83.50', 'change': '+0.12', 'up': True},
            ]
        })    


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get('message', '').lower()

    faqs = {
        'balance': 'You can check your account balance on your Dashboard after logging in.',
        'transfer': 'Go to Transfer Money section after login. Enter account number and amount.',
        'loan': 'Visit our Loans page to apply for Personal, Home, Car or Gold loans.',
        'complaint': 'I am sorry to hear that. Please describe your issue and I will raise a support ticket for you.',
        'interest': 'Our savings account offers 4.5% p.a. interest. FD rates start from 6.5% p.a.',
        'nri': 'We offer NRE, NRO and FCNR accounts for Non-Resident Indians. Visit our NRI Banking page.',
        'credit card': 'You can view your credit card details, transactions and statements after logging in.',
        'careers': 'We are hiring! Visit our Careers page to see current openings and apply.',
        'hours': 'Our branches are open Monday to Saturday, 9 AM to 5 PM.',
        'contact': 'You can reach us at support@sashaktbank.com or call 1800-XXX-XXXX.',
    }

    for keyword, response in faqs.items():
        if keyword in message:
            return jsonify({'reply': response})

    return jsonify({'reply': 'I understand your query. Let me connect you with our support team. Please call 1800-XXX-XXXX or email support@sashaktbank.com for immediate assistance.'})
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        aadhaar = request.form.get('aadhaar')
        address = request.form.get('address')
        account_type = request.form.get('account_type')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')

        if len(password) < 8:
            return render_template('register.html', error='Password must be at least 8 characters.')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error='Email already registered. Please login.')

        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create user
        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            aadhaar=aadhaar,
            address=address,
            password=hashed
        )
        db.session.add(new_user)
        db.session.commit()

        # Generate account number
        account_number = 'ACC' + ''.join(random.choices(string.digits, k=9))

        # Create bank account
        new_account = Account(
            user_id=new_user.id,
            account_number=account_number,
            account_type=account_type,
            balance=0.0,
            status='active'
        )
        db.session.add(new_account)
        db.session.commit()

        return render_template('register.html', success=f'Account created successfully! Your account number is {account_number}. Please login.')

    return render_template('register.html')
from datetime import datetime

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    accounts = Account.query.filter_by(user_id=user.id).all()

    recent_transactions = Transaction.query.filter(
        (Transaction.from_account == accounts[0].account_number) |
        (Transaction.to_account == accounts[0].account_number)
    ).order_by(Transaction.created_at.desc()).limit(5).all()

    return render_template('dashboard.html',
        user_name=user.full_name,
        user_email=user.email,
        accounts=accounts,
        recent_transactions=recent_transactions,
        current_date=datetime.now().strftime('%A, %d %B %Y')
    )
@app.route('/transfer')
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    accounts = Account.query.filter_by(user_id=user.id).all()
    recent_transfers = Transaction.query.filter_by(
        from_account=accounts[0].account_number
    ).order_by(Transaction.created_at.desc()).limit(3).all()
    return render_template('transfer.html',
        user_name=user.full_name,
        accounts=accounts,
        recent_transfers=recent_transfers
    )

@app.route('/get-account-name')
def get_account_name():
    account_number = request.args.get('account')
    account = Account.query.filter_by(account_number=account_number).first()
    if account:
        user = User.query.get(account.user_id)
        return jsonify({'name': user.full_name})
    return jsonify({'name': None})

@app.route('/do-transfer', methods=['POST'])
def do_transfer():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    data = request.get_json()
    from_acc_num = data.get('from_account')
    to_acc_num = data.get('to_account')
    amount = float(data.get('amount', 0))
    description = data.get('description', '')

    if amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid amount'})

    from_account = Account.query.filter_by(account_number=from_acc_num).first()
    to_account = Account.query.filter_by(account_number=to_acc_num).first()

    if not from_account:
        return jsonify({'success': False, 'message': 'Your account not found'})

    if not to_account:
        return jsonify({'success': False, 'message': 'Recipient account not found'})

    if from_acc_num == to_acc_num:
        return jsonify({'success': False, 'message': 'Cannot transfer to same account'})

    if from_account.balance < amount:
        return jsonify({'success': False, 'message': f'Insufficient balance. Available: ₹{from_account.balance:,.2f}'})

    from_account.balance -= amount
    to_account.balance += amount

    txn = Transaction(
        from_account=from_acc_num,
        to_account=to_acc_num,
        amount=amount,
        transaction_type='transfer',
        description=description
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'₹{amount:,.2f} transferred successfully to {to_acc_num}'
    })
@app.route('/get-balance')
def get_balance():
    if 'user_id' not in session:
        return jsonify({'balance': 0})
    account_number = request.args.get('account')
    account = Account.query.filter_by(account_number=account_number).first()
    if account:
        return jsonify({'balance': account.balance})
    return jsonify({'balance': 0})
@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    account = Account.query.filter_by(user_id=user.id).first()
    all_transactions = Transaction.query.filter(
        (Transaction.from_account == account.account_number) |
        (Transaction.to_account == account.account_number)
    ).order_by(Transaction.created_at.desc()).all()
    return render_template('transactions.html',
        user_name=user.full_name,
        account=account,
        transactions=all_transactions
    )
@app.route('/loans', methods=['GET', 'POST'])
def loans():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    user_loans = Loan.query.filter_by(user_id=user.id).order_by(Loan.created_at.desc()).all()

    if request.method == 'POST':
     loan_type = request.form.get('loan_type')
    amount = float(request.form.get('amount', 0))
    tenure = int(request.form.get('tenure', 0))
    interest_rate = float(request.form.get('interest_rate', 0))

    income_proof_path = None
    id_proof_path = None

    if 'income_proof' in request.files:
        file = request.files['income_proof']
        if file.filename != '':
            filename = secure_filename(f"income_{session['user_id']}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            income_proof_path = filename

    if 'id_proof' in request.files:
        file = request.files['id_proof']
        if file.filename != '':
            filename = secure_filename(f"id_{session['user_id']}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            id_proof_path = filename

    if amount <= 0 or tenure <= 0 or interest_rate <= 0:
        return render_template('loans.html',
            user_name=user.full_name,
            loans=user_loans,
            error='Please fill all fields correctly.')

    new_loan = Loan(
        user_id=user.id,
        loan_type=loan_type,
        amount=amount,
        tenure=tenure,
        interest_rate=interest_rate,
        status='pending',
        income_proof=income_proof_path,
        id_proof=id_proof_path
    )
    db.session.add(new_loan)
    db.session.commit()

    return render_template('loans.html',
        user_name=user.full_name,
        loans=Loan.query.filter_by(user_id=user.id).order_by(Loan.created_at.desc()).all(),
        success='Loan application submitted successfully with documents!')

    if amount <= 0 or tenure <= 0 or interest_rate <= 0:
            return render_template('loans.html',
                user_name=user.full_name,
                loans=user_loans,
                error='Please fill all fields correctly.')

            new_loan = Loan(
            user_id=user.id,
            loan_type=loan_type,
            amount=amount,
            tenure=tenure,
            interest_rate=interest_rate,
            status='pending'
        )
    db.session.add(new_loan)
    db.session.commit()

    return render_template('loans.html',
            user_name=user.full_name,
            loans=Loan.query.filter_by(user_id=user.id).order_by(Loan.created_at.desc()).all(),
            success='Loan application submitted successfully! We will review it shortly.')

    return render_template('loans.html',
        user_name=user.full_name,
        loans=user_loans
    )
@app.route('/credit-card')
def credit_card():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    card = CreditCard.query.filter_by(user_id=user.id).first()
    card_transactions = []
    if card:
        card_transactions = Transaction.query.filter(
            (Transaction.from_account == card.card_number) |
            (Transaction.to_account == card.card_number)
        ).order_by(Transaction.created_at.desc()).limit(10).all()
    return render_template('credit_card.html',
        user_name=user.full_name,
        card=card,
        card_transactions=card_transactions
    )

@app.route('/credit-card/pay', methods=['POST'])
def credit_card_pay():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    card = CreditCard.query.filter_by(user_id=user.id).first()
    amount = float(request.form.get('amount', 0))
    if card and amount > 0:
        card.outstanding_balance = max(0, card.outstanding_balance - amount)
        db.session.commit()

@app.route('/schemes')
def schemes():
    user_name = 'Guest'
    user_applications = []
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_name = user.full_name
        user_applications = SchemeApplication.query.filter_by(
            user_id=session['user_id']
        ).all()
    applied_schemes = [a.scheme_name for a in user_applications]
    return render_template('schemes.html',
        user_name=user_name,
        applied_schemes=applied_schemes
    )
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    accounts = Account.query.filter_by(user_id=user.id).all()
    return render_template('profile.html',
        user=user,
        accounts=accounts,
        update_success=request.args.get('update_success'),
        update_error=request.args.get('update_error'),
        password_success=request.args.get('password_success'),
        password_error=request.args.get('password_error')
    )

@app.route('/profile/update', methods=['POST'])
def profile_update():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    email = request.form.get('email')
    existing = User.query.filter_by(email=email).first()
    if existing and existing.id != user.id:
        return redirect(url_for('profile', update_error='Email already in use by another account.'))
    user.full_name = request.form.get('full_name')
    user.email = email
    user.phone = request.form.get('phone')
    user.address = request.form.get('address')
    db.session.commit()
    session['user_name'] = user.full_name
    session['user_email'] = user.email
    return redirect(url_for('profile', update_success='Profile updated successfully.'))

@app.route('/profile/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    current = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    confirm = request.form.get('confirm_password')
    if not bcrypt.checkpw(current.encode('utf-8'), user.password.encode('utf-8')):
        return redirect(url_for('profile', password_error='Current password is incorrect.'))
    if new_pass != confirm:
        return redirect(url_for('profile', password_error='New passwords do not match.'))
    if len(new_pass) < 8:
        return redirect(url_for('profile', password_error='Password must be at least 8 characters.'))
    user.password = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.session.commit()
    return redirect(url_for('profile', password_success='Password changed successfully.'))
@app.route('/rates')
def rates():
    user_name = 'Guest'
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_name = user.full_name
    loan_rates = InterestRate.query.filter_by(category='loan').all()
    deposit_rates = InterestRate.query.filter_by(category='deposit').all()
    gold_rates = InterestRate.query.filter_by(category='gold').all()
    return render_template('rates.html',
        user_name=user_name,
        loan_rates=loan_rates,
        deposit_rates=deposit_rates,
        gold_rates=gold_rates
    )
@app.route('/gold-rate')
def gold_rate():
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()
        usd_inr = data['rates']['INR']
        gold_per_gram_usd = 63.5
        gold_per_gram_inr = round(gold_per_gram_usd * usd_inr, 0)
        return jsonify({'rate': gold_per_gram_inr, 'status': 'success'})
    except:
        return jsonify({'rate': 7145, 'status': 'fallback'})

@app.route('/nri', methods=['GET', 'POST'])
def nri():
    user_name = 'Guest'
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_name = user.full_name

    enquiry_success = None
    enquiry_error = None

    if request.method == 'POST':
        email = request.form.get('email')
        account_type = request.form.get('account_type')

        existing = NriEnquiry.query.filter_by(
            email=email,
            account_type=account_type
        ).first()

        if existing:
            enquiry_error = f'You have already submitted an enquiry for {account_type} account. Our team will contact you soon.'
        else:
            enquiry = NriEnquiry(
                full_name=request.form.get('full_name'),
                email=email,
                phone=request.form.get('phone'),
                country=request.form.get('country'),
                account_type=account_type,
                message=request.form.get('message')
            )
            db.session.add(enquiry)
            db.session.commit()
            enquiry_success = 'Thank you! Our NRI banking specialist will contact you within 24 hours.'

    return render_template('nri.html',
        user_name=user_name,
        enquiry_success=enquiry_success,
        enquiry_error=enquiry_error
    )
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template('login.html', error='No account found with this email.')

        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return render_template('login.html', error='Incorrect password. Please try again.')

        if not user.is_active:
            return render_template('login.html', error='Your account has been deactivated. Please contact support.')

        session['user_id'] = user.id
        session['user_name'] = user.full_name
        session['user_email'] = user.email

        return redirect(url_for('dashboard'))

    return render_template('login.html')
@app.route('/get-loan-rate')
def get_loan_rate():
    loan_type = request.args.get('type')
    rate_map = {
        'Personal': 'Personal Loan',
        'Home': 'Home Loan',
        'Car': 'Car Loan',
        'Education': 'Education Loan',
        'Gold': 'Gold Loan'
    }
    product_name = rate_map.get(loan_type, 'Personal Loan')
    rate = InterestRate.query.filter_by(
        product_name=product_name,
        category='loan'
    ).first()
    if rate:
        return jsonify({'min_rate': rate.min_rate, 'max_rate': rate.max_rate})
    return jsonify({'min_rate': 10.5, 'max_rate': 18.0})
@app.route('/employee-portal')
def employee_portal():
    return render_template('employee_login.html')

@app.route('/employee/login', methods=['POST'])
def employee_login():
    email = request.form.get('email')
    password = request.form.get('password')
    employee = Employee.query.filter_by(email=email).first()
    if not employee:
        return render_template('employee_login.html', error='No employee found with this email.')
    if not bcrypt.checkpw(password.encode('utf-8'), employee.password.encode('utf-8')):
        return render_template('employee_login.html', error='Incorrect password.')
    if not employee.is_active:
        return render_template('employee_login.html', error='Your account has been deactivated.')
    session['emp_id'] = employee.id
    session['emp_name'] = employee.full_name
    session['emp_role'] = employee.role
    session['emp_dept'] = employee.department
    if employee.role == 'teller':
       return redirect('/employee/teller')
    elif employee.role == 'manager':
       return redirect('/employee/manager')
    elif employee.role == 'hr':
        return redirect('/employee/hr')
    return redirect(url_for('employee_portal'))
@app.route('/employee/teller')
def teller_dashboard():
    if 'emp_id' not in session or session.get('emp_role') != 'teller':
        return redirect('/employee-portal')
    total_customers = User.query.count()
    total_accounts = Account.query.count()
    today = datetime.now().date()
    today_transactions = Transaction.query.filter(
        db.func.date(Transaction.created_at) == today
    ).count()
    pending_tickets = SupportTicket.query.filter_by(status='open').count()
    recent_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).limit(10).all()
    return render_template('teller_dashboard.html',
        emp_name=session['emp_name'],
        current_date=datetime.now().strftime('%A, %d %B %Y'),
        total_customers=total_customers,
        total_accounts=total_accounts,
        today_transactions=today_transactions,
        pending_tickets=pending_tickets,
        recent_transactions=recent_transactions
    )

@app.route('/employee/search-customer')
def search_customer():
    if 'emp_id' not in session:
        return jsonify({'found': False})
    account_number = request.args.get('account')
    account = Account.query.filter_by(account_number=account_number).first()
    if account:
        user = User.query.get(account.user_id)
        return jsonify({
            'found': True,
            'name': user.full_name,
            'account_number': account.account_number,
            'account_type': account.account_type,
            'balance': account.balance,
            'status': account.status,
            'phone': user.phone
        })
    return jsonify({'found': False})

@app.route('/employee/process-transaction', methods=['POST'])
def process_transaction():
    if 'emp_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    data = request.get_json()
    account_number = data.get('account_number')
    txn_type = data.get('type')
    amount = float(data.get('amount', 0))
    description = data.get('description', '')
    account = Account.query.filter_by(account_number=account_number).first()
    if not account:
        return jsonify({'success': False, 'message': 'Account not found'})
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid amount'})
    if txn_type == 'withdrawal' and account.balance < amount:
        return jsonify({'success': False, 'message': f'Insufficient balance. Available: ₹{account.balance:,.2f}'})
    if txn_type == 'deposit':
        account.balance += amount
        txn = Transaction(
            from_account='CASH',
            to_account=account_number,
            amount=amount,
            transaction_type='deposit',
            description=description or 'Cash deposit by teller'
        )
    else:
        account.balance -= amount
        txn = Transaction(
            from_account=account_number,
            to_account='CASH',
            amount=amount,
            transaction_type='withdrawal',
            description=description or 'Cash withdrawal by teller'
        )
    db.session.add(txn)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': f'₹{amount:,.2f} {txn_type} processed successfully',
        'new_balance': account.balance
    })
@app.route('/employee/teller/transactions')
def teller_transactions():
    if 'emp_id' not in session or session.get('emp_role') != 'teller':
        return redirect('/employee-portal')

    transactions = Transaction.query.filter(
        (Transaction.from_account == 'CASH') |
        (Transaction.to_account == 'CASH')
    ).order_by(Transaction.created_at.desc()).all()

    today = datetime.now().date()
    today_processed = Transaction.query.filter(
        ((Transaction.from_account == 'CASH') |
        (Transaction.to_account == 'CASH')) &
        (db.func.date(Transaction.created_at) == today)
    ).count()

    total_deposit = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.from_account == 'CASH'
    ).scalar() or 0

    total_withdrawal = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.to_account == 'CASH'
    ).scalar() or 0

    all_accounts = Account.query.all()
    accounts_map = {acc.account_number: acc for acc in all_accounts}

    for acc in all_accounts:
        acc.user = User.query.get(acc.user_id)

    return render_template('teller_transactions.html',
        emp_name=session['emp_name'],
        transactions=transactions,
        accounts_map=accounts_map,
        total_processed=len(transactions),
        today_processed=today_processed,
        total_deposit=total_deposit,
        total_withdrawal=total_withdrawal
    )

@app.route('/employee/logout')
def employee_logout():
    session.pop('emp_id', None)
    session.pop('emp_name', None)
    session.pop('emp_role', None)
    session.pop('emp_dept', None)
    return redirect(url_for('employee_portal'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)
