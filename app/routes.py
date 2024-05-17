'''
Server routes implementation using Flask

'''

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import hashlib
import random
from .forms import LoginForm, RegistrationForm, BuyForm, RedeemForm
from .models import User, NFT, Fragment, Trade, TradeHistory
from . import db, app, processor


# Route for index.html
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Route for login.html
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is logged in, redirect to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    # Check whether it is a valid POST request and the data verification passes
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.user_email.data).first()
        if user and check_password_hash(user.passwd_hash, form.password.data):
            # If the user exists and the password is correct
            login_user(user, remember=form.remember_me.data)
            flash('Log in successfully as {}'.format(user.username), 'success')
            # Redirect to home page after successful login
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed: user does not exist/password is incorrect!', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


# Route for register.html
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, passwd_hash=hashed_password)
        new_user.set_balance(50)
        # Add user data to Database
        db.session.add(new_user)
        # Make sure to commit changes to the database
        db.session.commit()

        flash('Account created for {0}! You can now log in.'.format(form.username.data), 'success')
        return redirect(url_for('login'))  # Redirect to the login page after successful registration

    return render_template('register.html', title='Register', form=form)


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    trade_history = db.session.query(
        TradeHistory.trade_id,
        TradeHistory.frag_id,
        TradeHistory.frag_name,
        TradeHistory.price,
        TradeHistory.transaction_time,
        User.username.label('seller_username'),
    ).join(User, User.id == TradeHistory.seller).filter(TradeHistory.buyer == current_user.id).all()
    fragments=current_user.user_fragments
    collections = NFT.query.filter_by(completed=1, owner=current_user.id).all()
    return render_template('dashboard.html', trade_history=trade_history, fragments=fragments, collections=collections)


@app.route('/marketplace', methods=['GET'])
def marketplace():
    buy_form = BuyForm()
    redeem_form = RedeemForm()
    trades = Trade.query.all()
    users = User.query.all()
    nft = NFT.query.filter_by(completed=0).all()
    return render_template('marketplace.html', trades=trades, nft=nft ,buy_form=buy_form, redeem_form=redeem_form, user_num = len(users))



@app.route('/check_login', methods=['GET'])
def check_login():
    return jsonify({'is_logged_in': current_user.is_authenticated})


@app.route('/redeem', methods=['POST'])
def redeem():
    form = RedeemForm()
    print(1)
    if form.validate_on_submit():
        nft = NFT.query.get(form.nft_id.data)
        user = User.query.get(form.user.data)
        if not nft or not user:
            flash('NFT or user not found.', 'error')
            return redirect(url_for('marketplace'))
        
        fragments = Fragment.query.filter_by(img_id=nft.id, owner=user.id).all()
        piece_list = set()

        if len(fragments) < nft.pieces:
            flash('Not enough fragments to redeem.', 'error')
            return redirect(url_for('marketplace'))

      
        for fragment in fragments:
            if not fragment.verify_frag_name() or fragment.piece_number in piece_list:
                flash('Redeem verification failed.', 'error')
                return redirect(url_for('marketplace'))
            piece_list.add(fragment.piece_number)

        if len(piece_list) == nft.pieces and max(piece_list) == nft.pieces:
            # Process successful redemption here, such as transferring ownership, marking NFT as complete, etc.
            # Update NFT ownership and mark as completed
            nft.owner = user.id
            nft.completed = 1

            # Update user balance
            user.set_balance(float(user.balance) + float(nft.get_bonus))

             # Delete related fragments and trades
            for fragment in fragments:
                db.session.delete(fragment)

            # Commit all changes to the database
            db.session.commit()

            flash('Redemption successful.', 'success')
            return redirect(url_for('marketplace'))
        else:
            flash('Redeem verification failed.', 'error')
            return redirect(url_for('marketplace'))
        

    return render_template('marketplace.html')


@app.route('/privacy')
def privacy():
    return render_template('index.html')


@app.route('/terms')
def terms():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('index.html')


@app.route('/trade', methods=['POST'])
@login_required
def trade():
    data = request.get_json()
    if data:
        fragment_id = data.get('fragment_id')
        price = data.get('price')
        owner = data.get('owner')

        fragment = Fragment.query.get(fragment_id)
        if fragment is None:
            flash('Fragment not found', 'error')
            return redirect(url_for('dashboard'))
    
        # Fragment have been listed for transactions
        if Trade.query.get(fragment_id):
            flash('Fragment is currently for sale', 'error')
            return redirect(url_for('dashboard'))
        
        if str(owner) != str(current_user.id):
            flash('User information does not match', 'error')
            return redirect(url_for('dashboard'))

        # Create a new Trade object
        new_trade = Trade(id=fragment_id, owner=owner, listed_time=datetime.now())
        new_trade.set_price(price)

        # Add new transaction objects to the database
        db.session.add(new_trade)
        db.session.commit()
    
        flash('Trade created successfully', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid form data', 'error')
        return redirect(url_for('dashboard'))


@app.route('/trade/update_price/<string:frag_id>', methods=['POST'])
@login_required
def update_trade_price(frag_id):
    data = request.get_json()
    if data:
        status = data.get('status')
        price = data.get('price')
        owner = data.get('owner')

        # Retrieve the trade object
        trade = Trade.query.get(frag_id)
        if trade is None:
            flash('Trade not found', 'error')
            return redirect(url_for('dashboard'))
    
        # Check if current user is the owner of the fragment
        if str(current_user.id) != str(owner):
            flash('Owner information does not match', 'error')
            return redirect(url_for('dashboard'))

        # Update price
        if status == 'update':
            trade.set_price(price)
        elif status == 'cancel':
            db.session.delete(trade)
        db.session.commit()
        flash('Trade updated successfully', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid form data', 'error')
        return redirect(url_for('dashboard'))
        

@app.route('/buy', methods=['POST'])
def buy():
    form = BuyForm()
    if form.validate_on_submit():
        # Process Data
        frag = Fragment.query.get(form.fragment_id.data)
        buyer = User.query.get(form.buyer.data)
    
        if not frag or not buyer:
            flash('Invalid transaction details.', 'error')
            return redirect(url_for('marketplace'))
        
        # Get transaction information related to fragments
        trade = Trade.query.get(frag.id)
        # Confirm that the transaction information is valid
        if not trade:
            flash('No trade found for this fragment.', 'error')
            return redirect(url_for('marketplace'))

        # Check if the buyer is the current owner of the item
        if buyer.id == trade.owner:
            flash('You already own this fragment.', 'error')
            return redirect(url_for('marketplace'))
        elif buyer.balance < trade.price:
            flash('Insufficient balance.', 'error')
            return redirect(url_for('marketplace'))
        else:
            owner = User.query.get(trade.owner)
            if owner.balance + trade.price > 100000:
                owner.balance = 99999
            else:
                owner.balance += trade.price

            buyer.balance -= trade.price
            frag.owner = buyer.id

            # Add transaction history
            new_trade_history = TradeHistory(
                frag_id=frag.id,
                frag_name=frag.name,
                seller=owner.id,
                buyer=buyer.id,
                transaction_time=datetime.utcnow()
            )

            new_trade_history.set_price(trade.price)
            db.session.add(new_trade_history)

            # Since we have reassigned the fragment, we need to delete the existing trade
            db.session.delete(trade)

            # Commit all changes to the database
            db.session.commit()

            flash('Purchase successful!', 'success')
            return redirect(url_for('marketplace'))
        
    return render_template('marketplace.html', form=form)



@app.route('/upload', methods=['GET', 'POST'])
@login_required 
def upload():
    if current_user.username == 'root':
        if request.method == 'POST':
            file = request.files['file']
            num_parts = request.form.get('num_parts', type=int)
            
            if file and file.filename and processor.allowed_file(file.filename):
                filename = secure_filename(file.filename)  # NFT filename
                file_path = os.path.join(processor.upload_folder, filename)  # NFT filepath

                # Check if the file already exists
                if os.path.exists(file_path):
                    flash('A file with this name already exists. Please upload a file with a different name or delete the existing one.')
                    return redirect(request.url)

                save_result = processor.save_file(file)
                if save_result:
                    # Insert a new piece of data into the NFT table
                    img_hash_id = hashlib.sha256(filename.encode()).hexdigest() # NFT hash id
                    new_nft = NFT(id=img_hash_id, path=file_path, completed=False, pieces=num_parts, owner=0)
                    db.session.add(new_nft)

                    fragments = processor.split_image(file_path, num_parts)
                    for frag_data in fragments:
                        fragment_filename, fragment_path, piece_number = frag_data[0], frag_data[1], frag_data[2]
                        frag_hash_id = hashlib.sha256(fragment_filename.encode()).hexdigest() # Split hash id
                        new_fragment = Fragment(id = frag_hash_id, img_id = img_hash_id, path = fragment_path, piece_number = piece_number, owner = 0)
                        db.session.add(new_fragment)
                    db.session.commit()
                    

                    flash('File has been uploaded and processed successfully.')
                    return redirect(url_for('upload'))
                else:
                    flash('File format not supported.')
                    return redirect(request.url)
                
            else:
                flash('Invalid file or file format not supported.')
                return redirect(url_for('upload'))
        else:
            return render_template('upload.html')
    else:
        flash('You are not authorized to access this page.')
        return redirect(url_for('index'))
    

@app.route('/raffle', methods=['POST'])
@login_required
def raffle():
    # Lottery deduction
    deduction = 10
    current_balance = current_user.get_balance()
    if current_user.balance < deduction:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    current_user.set_balance(current_balance - deduction)
    available_fragments = Fragment.query.filter_by(owner=0).all()
    if not available_fragments:
        return jsonify({'error': 'No available fragments'}), 400
    
    selected_frag = random.choice(available_fragments)
    selected_frag.owner = current_user.id

    # Commit database changes
    db.session.commit()
    fragment_path = selected_frag.path.split('/static/')[-1]
    fragment_name = secure_filename(fragment_path.split('/')[-1])
    return jsonify({'fragment_path': fragment_path, 'fragment_name': fragment_name})


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))
    else:
        flash('No active session found - you were not logged in.', 'danger')
        return redirect(url_for('index'))


@app.route('/search_fragments', methods=['GET'])
def search_fragments():
    query = request.args.get('query', '').lower()

    if not query:
        trades = Trade.query.options(joinedload(Trade.fragment)).all()
    else:
        # 在数据库中直接进行不区分大小写的搜索，以防止SQL注入
        fragments = Fragment.query.options(joinedload(Fragment.trade)) \
                                   .filter(Fragment.name.ilike(f'%{query}%')).all()
        trades = [fragment.trade for fragment in fragments if fragment.trade]

    rendered = [render_template('_trade_card.html', trade=trade) for trade in trades]

    return jsonify({'html': rendered})
    
    '''
    if not query:
        trades = Trade.query.options(joinedload(Trade.fragment)).all()
    else:
        # Retrieve all fragments and filter them in Python
        fragments = Fragment.query.options(joinedload(Fragment.trade)).all()
        matching_fragments = [fragment for fragment in fragments if fragment.name and query in fragment.name.lower()]
        # Get the corresponding trades for those fragments
        trades = [fragment.trade for fragment in matching_fragments if fragment.trade]

    rendered = [render_template('_trade_card.html', trade=trade) for trade in trades]

    return jsonify({'html': rendered})
    '''