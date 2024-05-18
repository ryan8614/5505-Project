from flask import Blueprint, jsonify, request, flash, redirect, url_for, render_template
from flask_login import current_user, login_required
from datetime import datetime
from sqlalchemy.orm import joinedload
from ...forms import RedeemForm, BuyForm
from ...models import Fragment, Trade, NFT, User, TradeHistory
from ... import db
from . import trade_bp

@trade_bp.route('/trade', methods=['POST'])
@login_required
def trade():
    data = request.get_json()
    if data:
        fragment_id = data.get('fragment_id')
        price = data.get('price')
        owner = data.get('owner')

        # Convert price to floating point number
        try:
            price = float(price)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid price format'}), 400

        fragment = Fragment.query.get(fragment_id)
        if fragment is None:
            return jsonify({'status': 'error', 'message': 'Fragment not found'}), 404
    
        if Trade.query.get(fragment_id):
            return jsonify({'status': 'error', 'message': 'Fragment is currently for sale'}), 400
        
        if str(owner) != str(current_user.id):
            return jsonify({'status': 'error', 'message': 'User information does not match'}), 403

        # Create a new Trade object
        new_trade = Trade(id=fragment_id, owner=owner, listed_time=datetime.now())
        new_trade.set_price(price)

        # Add new transaction objects to the database
        db.session.add(new_trade)
        db.session.commit()
    
        return jsonify({
            'status': 'success', 
            'message': 'Trade created successfully',
            'new_status': 'For Sale', 
            'new_price': f'{price:.2f}'
        }), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid form data'}), 400

@trade_bp.route('/trade/update_price/<string:frag_id>', methods=['POST'])
@login_required
def update_trade_price(frag_id):
    data = request.get_json()
    if data:
        status = data.get('status')
        price = data.get('price')
        owner = data.get('owner')

        # Convert price to floating point number
        try:
            price = float(price)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid price format'}), 400

        # Retrieve the trade object
        trade = Trade.query.get(frag_id)
        if trade is None:
            return jsonify({'status': 'error', 'message': 'Trade not found'}), 404
    
        # Check if current user is the owner of the fragment
        if str(current_user.id) != str(owner):
            return jsonify({'status': 'error', 'message': 'Owner information does not match'}), 403

        # Update price
        if status == 'update':
            trade.set_price(price)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Trade updated successfully', 'new_price': f'{price:.2f}'}), 200
        elif status == 'cancel':
            db.session.delete(trade)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Trade cancelled successfully'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid form data'}), 400
     
@trade_bp.route('/redeem', methods=['POST'])
def redeem():
    form = RedeemForm()
    if form.validate_on_submit():
        print(form)
        nft = NFT.query.get(form.nft_id.data)
        user = User.query.get(form.user.data)
        if not nft or not user:
            flash('NFT or user not found.', 'error')
            return redirect(url_for('pages.marketplace'))
        
        fragments = Fragment.query.filter_by(img_id=nft.id, owner=user.id).all()
        piece_list = set()

        if len(fragments) < nft.pieces:
            flash('Not enough fragments to redeem.', 'error')
            return redirect(url_for('pages.marketplace'))

    
        for fragment in fragments:
            if not fragment.verify_frag_name() or fragment.piece_number in piece_list:
                flash('Redeem verification failed.', 'error')
                return redirect(url_for('pages.marketplace'))
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
            return redirect(url_for('pages.marketplace'))
        else:
            flash('Redeem verification failed.', 'error')
            return redirect(url_for('pages.marketplace'))
        
    else:
        flash('Form submission failed', 'error')
        return redirect(url_for('pages.marketplace'))
    
@trade_bp.route('/search_fragments', methods=['GET'])
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
  
@trade_bp.route('/get_fragments', methods=['GET'])
@login_required
def get_fragments():
    fragments = current_user.user_fragments
    fragments_data = []
    for fragment in fragments:
        # Check if the price is of a type convertible to a float
        try:
            price = float(fragment.trade_price[1]) if fragment.trade_price[0] == 'For Sale' else ''
            price = f"{price:.2f}" if price != '' else ''
        except ValueError:
            price = ''  # If the conversion fails, set the price to an empty string

        fragments_data.append({
            'path': fragment.path,
            'id': fragment.id,
            'name': fragment.name,
            'status': fragment.trade_price[0],
            'price': price
        })
    return jsonify(fragments_data)

@trade_bp.route('/buy', methods=['POST'])
def buy():
    form = BuyForm()
    if form.validate_on_submit():
        # Process Data
        frag = Fragment.query.get(form.fragment_id.data)
        buyer = User.query.get(form.buyer.data)
    
        if not frag or not buyer:
            flash('Invalid transaction details.', 'error')
            return redirect(url_for('pages.marketplace'))
        
        # Get transaction information related to fragments
        trade = Trade.query.get(frag.id)
        # Confirm that the transaction information is valid
        if not trade:
            flash('No trade found for this fragment.', 'error')
            return redirect(url_for('pages.marketplace'))

        # Check if the buyer is the current owner of the item
        if buyer.id == trade.owner:
            flash('You already own this fragment.', 'error')
            return redirect(url_for('pages.marketplace'))
        elif buyer.balance < trade.price:
            flash('Insufficient balance.', 'error')
            return redirect(url_for('pages.marketplace'))
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
            return redirect(url_for('pages.marketplace'))
        
    return render_template('marketplace.html', form=form)
