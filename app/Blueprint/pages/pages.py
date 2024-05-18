from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ...models import TradeHistory, Trade
from ...models import User, NFT, Fragment
from ...forms import BuyForm, RedeemForm
from ... import db
from . import pages_bp

# Route for ind
@pages_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@pages_bp.route('/dashboard', methods=['GET'])
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
    available_fragments = Fragment.query.filter_by(owner=0).all()
    return render_template('dashboard.html', trade_history=trade_history, fragments=fragments, collections=collections, available_fragments=available_fragments)

@pages_bp.route('/marketplace', methods=['GET'])
def marketplace():
    buy_form = BuyForm()
    redeem_form = RedeemForm()
    trades = Trade.query.all()
    users = User.query.all()
    nft = NFT.query.filter_by(completed=0).all()
    return render_template('marketplace.html', trades=trades, nft=nft ,buy_form=buy_form, redeem_form=redeem_form, user_num = len(users))

@pages_bp.route('/privacy', methods = ['GET'])
def privacy():
    return render_template('index.html')

@pages_bp.route('/terms')
def terms():
    return render_template('index.html')

@pages_bp.route('/about')
def about():
    return render_template('index.html')


