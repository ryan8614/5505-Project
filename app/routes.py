'''
Server routes implementation using Flask

'''

from flask import current_app as app, render_template, flash, redirect, url_for, request, jsonify, g
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import hashlib
import random
from sqlalchemy.orm import joinedload

from .forms import LoginForm, RegistrationForm, BuyForm, RedeemForm
from .models import User, NFT, Fragment, Trade, TradeHistory
from . import db

