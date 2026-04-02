from app import app, db, User, Account, Employee, Transaction, Loan, CreditCard, JobPosting
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

with app.app_context():

    # Users
    users = [
        User(full_name='Rahul Sharma', email='demouser1bank@gmail.com', password=hash_password('password123'), phone='9800000001', aadhaar='1234-5678-9012', address='123 Demo Street, Mumbai', is_active=True),
        User(full_name='Priya Patel', email='demouser2bank@gmail.com', password=hash_password('password123'), phone='9800000002', aadhaar='2345-6789-0123', address='456 Test Avenue, Delhi', is_active=True),
        User(full_name='Amit Verma', email='demouser3bank@gmail.com', password=hash_password('password123'), phone='9800000003', aadhaar='3456-7890-1234', address='789 Sample Road, Bangalore', is_active=True),
        User(full_name='Sneha Gupta', email='demouser4bank@gmail.com', password=hash_password('password123'), phone='9800000004', aadhaar='4567-8901-2345', address='321 Fake Lane, Chennai', is_active=True),
    ]
    db.session.add_all(users)
    db.session.commit()

    # Accounts
    accounts = [
        Account(user_id=1, account_number='ACC001001', account_type='Savings', balance=50000.0, status='active'),
        Account(user_id=2, account_number='ACC001002', account_type='Current', balance=120000.0, status='active'),
        Account(user_id=3, account_number='ACC001003', account_type='Savings', balance=35000.0, status='active'),
        Account(user_id=4, account_number='ACC001004', account_type='Savings', balance=80000.0, status='active'),
    ]
    db.session.add_all(accounts)
    db.session.commit()

    # Transactions
    transactions = [
        Transaction(from_account='ACC001001', to_account='ACC001002', amount=5000.0, transaction_type='transfer', description='Rent payment'),
        Transaction(from_account='ACC001002', to_account='ACC001003', amount=2000.0, transaction_type='transfer', description='Shopping'),
        Transaction(from_account='ACC001003', to_account='ACC001001', amount=1000.0, transaction_type='transfer', description='Lunch split'),
        Transaction(from_account='ACC001004', to_account='ACC001002', amount=3000.0, transaction_type='transfer', description='Bill payment'),
    ]
    db.session.add_all(transactions)
    db.session.commit()

    # Employees
    employees = [
        Employee(full_name='Vikram Singh', email='demoteller.bank@gmail.com', password=hash_password('emp123'), role='teller', department='Operations', is_active=True),
        Employee(full_name='Anjali Mehta', email='demomanager.bank@gmail.com', password=hash_password('emp123'), role='manager', department='Management', is_active=True),
        Employee(full_name='Ravi Kumar', email='demohr.bank@gmail.com', password=hash_password('emp123'), role='hr', department='Human Resources', is_active=True),
    ]
    db.session.add_all(employees)
    db.session.commit()

    # Loans
    loans = [
        Loan(user_id=1, loan_type='Personal', amount=100000.0, tenure=24, interest_rate=10.5, status='approved'),
        Loan(user_id=2, loan_type='Home', amount=2000000.0, tenure=240, interest_rate=8.5, status='pending'),
        Loan(user_id=3, loan_type='Car', amount=500000.0, tenure=60, interest_rate=9.0, status='rejected'),
    ]
    db.session.add_all(loans)
    db.session.commit()

    # Credit Cards
    from datetime import date
    cards = [
        CreditCard(user_id=1, card_number='4111111111111001', credit_limit=100000.0, outstanding_balance=15000.0, due_date=date(2025, 5, 15), status='active'),
        CreditCard(user_id=2, card_number='4111111111111002', credit_limit=200000.0, outstanding_balance=45000.0, due_date=date(2025, 5, 20), status='active'),
    ]
    db.session.add_all(cards)
    db.session.commit()

    # Job Postings
    jobs = [
        JobPosting(title='Software Engineer', department='IT', location='Mumbai', job_type='Full-time', description='Build and maintain banking software systems.', is_active=True),
        JobPosting(title='HR Executive', department='Human Resources', location='Delhi', job_type='Full-time', description='Manage recruitment and employee relations.', is_active=True),
        JobPosting(title='Bank Teller', department='Operations', location='Bangalore', job_type='Full-time', description='Handle customer transactions at the counter.', is_active=True),
    ]
    db.session.add_all(jobs)
    db.session.commit()

    print("All dummy data inserted successfully!")