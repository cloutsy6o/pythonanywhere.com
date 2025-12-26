from flask import Flask, session, redirect, render_template, request, url_for, flash, Response, jsonify
from flask_bcrypt import Bcrypt
import os
import sys
from datetime import datetime
from order_routes import order_bp
from upload_routes import upload_bp
from admin_routes import admin_bp
from product_routes import product_bp
from cart_routes import cart_bp

# Try to import modules
def safe_import(module_name, blueprint_name):
    try:
        module = __import__(module_name)
        bp = getattr(module, blueprint_name)
        print(f"✅ {module_name} blueprint registered")
        return bp, True
    except Exception as e:
        print(f"⚠️ {module_name} not available: {e}")
        return None, False

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-to-very-long-random-string')
bcrypt = Bcrypt(app)

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(order_bp)
app.register_blueprint(upload_bp)

# Dynamically register available blueprints
modules_to_register = [
    ('customer_auth', 'customer_bp'),
    ('ticket_routes', 'ticket_bp'),
    ('address_routes', 'address_bp')
]

for module_name, bp_name in modules_to_register:
    bp, available = safe_import(module_name, bp_name)
    if available and bp:
        app.register_blueprint(bp)

# Hardcoded admin user
USER = "username"
HASH = 'password'

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for SEO"""
    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, titel, erstellt_am FROM produkte")
        products = cursor.fetchall()
        cursor.close()
        conn.close()

        xml = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

        # Add static pages
        pages = [
            ('/', datetime.now().strftime('%Y-%m-%d'), 'daily', '1.0'),
            ('/startseite', datetime.now().strftime('%Y-%m-%d'), 'daily', '1.0'),
            ('/cart', datetime.now().strftime('%Y-%m-%d'), 'weekly', '0.7'),
            ('/customer/login', datetime.now().strftime('%Y-%m-%d'), 'monthly', '0.5'),
        ]

        for url, lastmod, changefreq, priority in pages:
            xml.append(f'''  <url>
    <loc>{request.url_root.rstrip("/")}{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>''')

        # Add product pages
        for product in products:
            lastmod = product["erstellt_am"].strftime("%Y-%m-%d") if product["erstellt_am"] else datetime.now().strftime("%Y-%m-%d")
            xml.append(f'''  <url>
    <loc>{request.url_root.rstrip("/")}/product/{product["id"]}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')

        xml.append('</urlset>')
        return Response('\n'.join(xml), mimetype='application/xml')

    except Exception as e:
        return str(e), 500

@app.route('/robots.txt')
def robots():
    """Generate robots.txt"""
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /customer/login
Disallow: /cart/checkout

Sitemap: {request.url_root.rstrip('/')}/sitemap.xml
"""
    return Response(content, mimetype='text/plain')

@app.route('/search')
def search():
    """SEO-friendly search results"""
    query = request.args.get('q', '').strip()

    if not query:
        return redirect('/')

    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Search products with prices
        cursor.execute("""
            SELECT p.*,
                   (SELECT MIN(pp.aktueller_preis)
                    FROM produkt_preise pp
                    WHERE pp.produkt_id = p.id) as min_price
            FROM produkte p
            WHERE p.titel LIKE %s OR p.beschreibung LIKE %s
            ORDER BY p.erstellt_am DESC
        """, (f'%{query}%', f'%{query}%'))

        results = cursor.fetchall()

        # Get prices for each product
        for product in results:
            cursor.execute("""
                SELECT s.name, pp.aktueller_preis, pp.link
                FROM produkt_preise pp
                JOIN shops s ON pp.shop_id = s.id
                WHERE pp.produkt_id = %s
                ORDER BY pp.aktueller_preis
            """, (product['id'],))
            product['prices'] = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('search/results.html',
                             query=query,
                             results=results,
                             title=f'Suchergebnisse für "{query}" - Günstiger Gefunden')

    except Exception as e:
        flash(f'Fehler bei der Suche: {str(e)}', 'error')
        return redirect('/')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with SEO optimization"""
    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM produkte WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            flash('Produkt nicht gefunden.', 'error')
            return redirect('/')

        # Get prices from all shops
        cursor.execute("""
            SELECT s.name, s.id as shop_id, pp.aktueller_preis, pp.link
            FROM produkt_preise pp
            JOIN shops s ON pp.shop_id = s.id
            WHERE pp.produkt_id = %s
            ORDER BY pp.aktueller_preis
        """, (product_id,))

        prices = cursor.fetchall()

        # Get related products
        cursor.execute("""
            SELECT p.id, p.titel, p.bild,
                   (SELECT MIN(pp.aktueller_preis)
                    FROM produkt_preise pp
                    WHERE pp.produkt_id = p.id) as min_price
            FROM produkte p
            WHERE p.id != %s
            ORDER BY RAND()
            LIMIT 4
        """, (product_id,))

        related = cursor.fetchall()
        cursor.close()
        conn.close()

        # Handle image path
        bild_pfad = product['bild']
        if not bild_pfad.startswith('/'):
            bild_pfad = '/' + bild_pfad

        server_pfad = os.path.join(app.root_path, 'static', bild_pfad.lstrip('/'))
        if not os.path.exists(server_pfad):
            bild_pfad = '/uploads/platzhalter.jpg'

        product['bild_pfad'] = bild_pfad

        return render_template('product/detail.html',
                             product=product,
                             prices=prices,
                             related=related,
                             title=f"{product['titel']} - Preisvergleich - Günstiger Gefunden")

    except Exception as e:
        flash(f'Fehler: {str(e)}', 'error')
        return redirect('/')

# Routes
@app.route('/')
def index():
    return redirect('/startseite')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ADMIN LOGIN ONLY - Customers use /customer/login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_page = request.form.get('next', 'admin/panel')

        if username == USER and bcrypt.check_password_hash(HASH, password):
            session['logged_in'] = True
            session['user_type'] = 'admin'
            return redirect(f'/{next_page}')
        else:
            error = "Falscher Benutzername oder Passwort."
            return render_template('login.html', error=error, next=request.form.get('next', ''))

    return render_template('login.html', next=request.args.get('next', ''))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/startseite')
def startseite():
    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get products with star ratings
        cursor.execute("""
            SELECT id, titel, beschreibung, bild,
                   bewertung_durchschnitt, bewertung_anzahl
            FROM produkte
            ORDER BY erstellt_am DESC
        """)
        produkte = cursor.fetchall()

        auskommentierte_ids = [7, 8, 9, 11, 12, 13, 14, 15]
        gefilterte_produkte = []

        for produkt in produkte:
            if int(produkt['id']) not in auskommentierte_ids:
                # Get prices for each shop
                cursor.execute("""
                    SELECT shop_id, link, aktueller_preis
                    FROM produkt_preise
                    WHERE produkt_id = %s
                """, (int(produkt['id']),))
                preise = cursor.fetchall()
                preise_dict = {str(preis['shop_id']): preis for preis in preise}
                produkt['preise'] = preise_dict

                # Handle image path
                bild_pfad = produkt['bild']
                if not bild_pfad.startswith('/'):
                    bild_pfad = '/' + bild_pfad

                if 'bild_688f223c119fa4.19974504.jpg' in produkt['bild']:
                    bild_pfad = '/uploads/lueckenreinigungsbuersten.jpg'

                server_pfad = os.path.join(app.root_path, 'static', bild_pfad.lstrip('/'))
                if not os.path.exists(server_pfad):
                    bild_pfad = '/uploads/platzhalter.jpg'

                produkt['bild_pfad'] = bild_pfad

                # Ensure star ratings are properly formatted
                produkt['bewertung_durchschnitt'] = float(produkt['bewertung_durchschnitt'] or 0)
                produkt['bewertung_anzahl'] = int(produkt['bewertung_anzahl'] or 0)

                gefilterte_produkte.append(produkt)

        cursor.close()
        conn.close()
        return render_template('startseite.html',
                             produkte=gefilterte_produkte,
                             title='Günstiger Gefunden - Preisvergleich für Amazon, Otto, AliExpress & Temu')

    except Exception as e:
        import traceback
        print(f"DEBUG TRACEBACK: {traceback.format_exc()}")
        return f"❌ Datenbankfehler: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=8080)
