from flask import Blueprint, render_template, request, session, redirect, flash
from db import get_db_connection
import os
import uuid
from functools import wraps

product_bp = Blueprint('product', __name__, url_prefix='/product')

# Admin login required decorator
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('user_type') != 'admin':
            flash('🔒 Admin access required. Please login.', 'error')
            return redirect(f'/login?next={request.url}')
        return f(*args, **kwargs)
    return decorated_function

@product_bp.route('/add', methods=['GET', 'POST'])
@admin_login_required
def add_product():
    # Check if user is logged in (already handled by decorator, but keep for safety)
    if not session.get('logged_in'):
        return redirect('/login?next=product/add')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get shops for dropdown
        cursor.execute("SELECT id, name FROM shops ORDER BY id")
        shops = cursor.fetchall()

        if request.method == 'POST' and 'submit' in request.form:
            # Get form data
            titel = request.form.get('titel')
            beschreibung = request.form.get('beschreibung', '')
            bewertung_durchschnitt = request.form.get('bewertung_durchschnitt')
            bewertung_anzahl = request.form.get('bewertung_anzahl')
            label = request.form.get('label', '')

            # Shop prices and links
            preis_otto = request.form.get('preis_otto')
            link_otto = request.form.get('link_otto', '')
            preis_amazon = request.form.get('preis_amazon')
            link_amazon = request.form.get('link_amazon', '')
            preis_aliexpress = request.form.get('preis_aliexpress')
            link_aliexpress = request.form.get('link_aliexpress', '')
            aliexpress_id = request.form.get('aliexpress_id', '')
            preis_temu = request.form.get('preis_temu')
            link_temu = request.form.get('link_temu', '')

            # Handle image upload
            bild_file = request.files.get('bild')
            if not bild_file or bild_file.filename == '':
                flash('❌ Bitte wählen Sie ein Produktbild aus.', 'error')
                return render_template('add-product.html', shops=shops)

            # Validate image
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
            file_ext = bild_file.filename.rsplit('.', 1)[1].lower() if '.' in bild_file.filename else ''
            if file_ext not in allowed_extensions:
                flash('❌ Ungültiges Bildformat. Erlaubt: JPG, JPEG, PNG, GIF, WebP', 'error')
                return render_template('add-product.html', shops=shops)

            # Generate unique filename
            filename = f"bild_{uuid.uuid4().hex}.{file_ext}"
            upload_path = os.path.join('static', 'uploads', filename)

            try:
                # Save image
                bild_file.save(upload_path)

                # Start transaction
                conn.start_transaction()

                # Insert product
                cursor.execute("""
                    INSERT INTO produkte (titel, beschreibung, bild, label, bewertung_durchschnitt, bewertung_anzahl, erstellt_am)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (
                    titel,
                    beschreibung,
                    f"uploads/{filename}",
                    label if label else None,
                    float(bewertung_durchschnitt) if bewertung_durchschnitt else None,
                    int(bewertung_anzahl) if bewertung_anzahl else None
                ))

                produkt_id = cursor.lastrowid

                # Insert prices for each shop
                shops_data = [
                    (1, preis_otto, link_otto, None),  # Otto
                    (2, preis_amazon, link_amazon, None),  # Amazon
                    (3, preis_aliexpress, link_aliexpress, aliexpress_id),  # AliExpress
                    (4, preis_temu, link_temu, None)  # Temu
                ]

                for shop_id, preis, link, ali_id in shops_data:
                    if preis and float(preis) > 0:
                        cursor.execute("""
                            INSERT INTO produkt_preise (produkt_id, shop_id, link, aliexpress_id, aktueller_preis, letzte_pruefung)
                            VALUES (%s, %s, %s, %s, %s, NOW())
                        """, (produkt_id, shop_id, link, ali_id, float(preis)))

                # Commit transaction
                conn.commit()
                flash('✅ Produkt erfolgreich gespeichert!', 'success')

            except Exception as e:
                # Rollback on error
                conn.rollback()
                # Delete uploaded file if transaction failed
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                flash(f'❌ Fehler beim Speichern: {str(e)}', 'error')

        cursor.close()
        conn.close()

        return render_template('add-product.html', shops=shops)

    except Exception as e:
        flash(f'❌ Datenbankfehler: {str(e)}', 'error')
        return render_template('add-product.html', shops=[])
