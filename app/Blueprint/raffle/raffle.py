from flask import jsonify, request, flash, redirect, url_for, render_template
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from ...models import Fragment, NFT
from ... import db
from . import raffle_bp, processor
import random, os
import hashlib


@raffle_bp.route('/raffle', methods=['POST'])
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
    fragment_id = selected_frag.id
    return jsonify({'fragment_path': fragment_path, 'fragment_name': fragment_name, 'fragment_id':fragment_id})


@raffle_bp.route('/upload', methods=['GET', 'POST'])
@login_required 
def upload():
    if current_user.username == 'root':
        if request.method == 'POST':
            file = request.files['file']
            num_parts = request.form.get('num_parts', type=int)
            bonus = request.form.get('bonus', type=float)
            
            if file and file.filename and processor.allowed_file(file.filename):
                filename = secure_filename(file.filename)  # NFT filename
                file_path = os.path.join(processor.upload_folder, filename)  # NFT filepath

                # Check if the file already exists
                if os.path.exists(file_path):
                    flash('A file with this name already exists. Please upload a file with a different name or delete the existing one.', 'danger')
                    return redirect(request.url)

                save_result = processor.save_file(file)
                if save_result:
                    # Insert a new piece of data into the NFT table
                    img_hash_id = hashlib.sha256(filename.encode()).hexdigest() # NFT hash id
                    new_nft = NFT(id=img_hash_id, path=file_path, completed=False, pieces=num_parts, owner=0)
                    new_nft.set_bonus(bonus)
                    db.session.add(new_nft)

                    fragments = processor.split_image(file_path, num_parts)
                    for frag_data in fragments:
                        fragment_filename, fragment_path, piece_number = frag_data[0], frag_data[1], frag_data[2]
                        frag_hash_id = hashlib.sha256(fragment_filename.encode()).hexdigest() # Split hash id
                        new_fragment = Fragment(id = frag_hash_id, img_id = img_hash_id, path = fragment_path, piece_number = piece_number, owner = 0)
                        db.session.add(new_fragment)
                    db.session.commit()
                    

                    flash('File has been uploaded and processed successfully.', 'success')
                    return redirect(url_for('raffle.upload'))
                else:
                    flash('File format not supported.', 'danger')
                    return redirect(request.url)
                
            else:
                flash('Invalid file or file format not supported.', 'danger')
                return redirect(url_for('raffle.upload'))
        else:
            return render_template('upload.html')
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('pages.index'))
    