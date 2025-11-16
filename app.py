"""
Main Flask Application for The Smiling Tear Foundation
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from database import get_db, init_db
from werkzeug.security import generate_password_hash, check_password_hash

from flask_mail import Mail, Message
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from twilio.rest import Client
import random


app = Flask(__name__)

app.config['SECRET_KEY'] = ...
app.config['UPLOAD_FOLDER'] = ...
mail = Mail(app)



# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

#otp 
TWILIO_SID = "your_sid_here"
TWILIO_AUTH = "your_auth_token_here"
TWILIO_NUMBER = "+1234567890"


mail = Mail(app)

# Utility function to load JSON data
def load_json_data(filename):
    """Load data from JSON file"""
    try:
        with open(f'data/{filename}', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

# Context processor to make data available to all templates
@app.context_processor
def inject_global_data():
    """Inject global data into all templates"""
    config_data = load_json_data('config.json')
    return {
        'site_info': config_data.get('siteInfo', {}),
        'contact_info': config_data.get('contact', {}),
        'social_media': config_data.get('socialMedia', {}),
        'current_year': datetime.now().year
    }

# Template filters
@app.template_filter('format_date')
def format_date(date_string):
    """Format date string to readable format"""
    try:
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_string

@app.template_filter('format_currency')
def format_currency(amount):
    """Format amount to Indian currency"""
    return f"₹{amount:,.0f}"

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    config_data = load_json_data('config.json')
    programs_data = load_json_data('programs.json')
    events_data = load_json_data('events.json')
    blog_data = load_json_data('blog-posts.json')
    
    # Get featured programs (first 2)
    featured_programs = programs_data.get('programs', [])[:2]
    
    # Get upcoming events (first 3)
    upcoming_events = [e for e in events_data.get('events', []) if e.get('status') == 'upcoming'][:3]
    
    # Get latest blog posts (first 3)
    latest_posts = blog_data.get('posts', [])[:3]
    
    return render_template('index.html',
                         hero=config_data.get('hero', {}),
                         stats=config_data.get('stats', {}),
                         mission=config_data.get('mission', {}),
                         featured_programs=featured_programs,
                         upcoming_events=upcoming_events,
                         latest_posts=latest_posts)


# signup route

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db()
        cur = conn.cursor()

        # Check approval
        cur.execute("SELECT * FROM volunteer_applications WHERE email=? AND status='approved'", (email,))
        approved = cur.fetchone()

        if not approved:
            flash("You must be an approved volunteer before signing up.", "error")
            return redirect(url_for('signup'))

        # Check duplicate
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        if cur.fetchone():
            flash("Account already exists.", "error")
            return redirect(url_for('signup'))

        # Insert user
        cur.execute("""
            INSERT INTO users (username, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, password, "volunteer"))

        conn.commit()
        conn.close()

        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')




@app.route('/about')
def about():
    """About page"""
    config_data = load_json_data('config.json')
    team_data = load_json_data('team-members.json')
    
    return render_template('about.html',
                         about=config_data.get('about', {}),
                         team_members=team_data.get('team', []))


@app.route('/programs')
def programs():
    """Programs listing page"""
    programs_data = load_json_data('programs.json')
    return render_template('programs.html',
                         programs=programs_data.get('programs', []))


@app.route('/programs/<slug>')
def program_detail(slug):
    """Single program detail page"""
    programs_data = load_json_data('programs.json')
    program = next((p for p in programs_data.get('programs', []) if p['slug'] == slug), None)
    
    if not program:
        return render_template('404.html'), 404
    
    return render_template('program_detail.html', program=program)




@app.route('/events')
def events():
    """Events listing page"""
    events_data = load_json_data('events.json')
    all_events = events_data.get('events', [])
    
    # Separate upcoming and past events
    upcoming = [e for e in all_events if e.get('status') == 'upcoming']
    past = [e for e in all_events if e.get('status') == 'past']
    
    return render_template('events.html',
                         upcoming_events=upcoming,
                         past_events=past)


@app.route('/events/<slug>')
def event_detail(slug):
    """Single event detail page"""
    events_data = load_json_data('events.json')
    event = next((e for e in events_data.get('events', []) if e['slug'] == slug), None)
    
    if not event:
        return render_template('404.html'), 404
    
    return render_template('event_detail.html', event=event)


@app.route('/blog')
def blog():
    """Blog listing page"""
    blog_data = load_json_data('blog-posts.json')
    
    # Filter by category if provided
    category = request.args.get('category')
    posts = blog_data.get('posts', [])
    
    if category:
        posts = [p for p in posts if p.get('category') == category]
    
    return render_template('blog.html', posts=posts, selected_category=category)


@app.route('/blog/<slug>')
def blog_detail(slug):
    """Single blog post detail page"""
    blog_data = load_json_data('blog-posts.json')
    post = next((p for p in blog_data.get('posts', []) if p['slug'] == slug), None)
    
    if not post:
        return render_template('404.html'), 404
    
    # Get related posts (same category, exclude current)
    related_posts = [p for p in blog_data.get('posts', []) 
                    if p.get('category') == post.get('category') and p['id'] != post['id']][:3]
    
    return render_template('blog_detail.html', post=post, related_posts=related_posts)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form submission"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Save to JSON file (or database)
        save_contact_submission(name, email, phone, message)
        
        # Send email notification
        try:
            send_contact_email(name, email, phone, message)
            flash('Thank you for contacting us! We will get back to you soon.', 'success')
        except Exception as e:
            app.logger.error(f'Error sending email: {str(e)}')
            flash('Your message has been received, but there was an issue with email notification.', 'warning')
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html')


@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    """Volunteer page with application form"""
    config_data = load_json_data('config.json')
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        city = request.form.get('city')
        interests = request.form.getlist('interests')
        message = request.form.get('message')
        
        # Save volunteer application
        save_volunteer_application(name, email, phone, city, interests, message)
        
        # Send confirmation email
        try:
            send_volunteer_email(name, email)
            flash('Thank you for your interest in volunteering! We will contact you soon.', 'success')
        except Exception as e:
            app.logger.error(f'Error sending email: {str(e)}')
            flash('Your application has been received!', 'success')
        
        return redirect(url_for('volunteer'))
    
    return render_template('volunteer.html',
                         volunteer_benefits=config_data.get('volunteerBenefits', []))



@app.route('/donate', methods=['GET', 'POST'])
def donate():
    """Donation page"""
    config_data = load_json_data('config.json')
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        program = request.form.get('program')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        is_anonymous = request.form.get('anonymous') == 'on'
        
        # Simulate payment success
        payment_status = request.form.get('payment_status', 'success')

        # Save donation (your existing logic)
        donation_id = save_donation(amount, program, name, email, phone, is_anonymous)

        if payment_status == 'success':
            # Generate receipt PDF in memory
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(200, 750, "Donation Receipt")
            c.setFont("Helvetica", 12)
            
            c.drawString(50, 720, f"Receipt ID: {donation_id}")
            c.drawString(50, 700, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(50, 680, f"Name: {name if not is_anonymous else 'Anonymous'}")
            c.drawString(50, 660, f"Email: {email}")
            c.drawString(50, 640, f"Phone: {phone}")
            c.drawString(50, 620, f"Program: {program}")
            c.drawString(50, 600, f"Amount Donated: ₹{amount}")
            
            c.line(50, 580, 550, 580)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 560, "Organization Details:")
            c.setFont("Helvetica", 11)
            c.drawString(50, 540, "Smiling Tears Foundation")
            c.drawString(50, 525, "Reg. No: 1234")
            c.drawString(50, 510, "Address: Laxmi Nagar, Delhi")
            c.drawString(50, 495, "Contact: 9009664469")
            c.drawString(50, 480, "Email: smilingtearsfoundation@gmail.com")
            
            c.showPage()
            c.save()
            buffer.seek(0)

            # Send file as downloadable PDF
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"Donation_Receipt_{donation_id}.pdf",
                mimetype='application/pdf'
            )
        else:
            flash('Payment was unsuccessful. Please try again.', 'danger')
            return redirect(url_for('donate'))

    return render_template(
        'donate.html',
        donation_tiers=config_data.get('donationTiers', []),
        payment_methods=config_data.get('paymentMethods', [])
    )


# ============================================================================
# API ROUTES 
# ============================================================================

# Login Route 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            if user['role'] == 'manager':
                return redirect(url_for('manager_dashboard'))
            return redirect(url_for('volunteer_dashboard'))

        flash("Invalid credentials.", "error")
        return redirect(url_for('login'))


        conn.close()

        if user:
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            if user['role'] == 'manager':
                return redirect(url_for('manager_dashboard'))
            return redirect(url_for('volunteer_dashboard'))

        flash("Invalid credentials.", "error")
        return redirect(url_for('login'))

    return render_template('login.html')


# logout route 

@app.route('/logout')
def logout():
    session.clear()  # remove all session data
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))


# SEND OTP 

def send_otp(phone):
    otp = random.randint(100000, 999999)

    client = Client(TWILIO_SID, TWILIO_AUTH)
    client.messages.create(
        body=f"Your Smiling Tears password reset OTP is {otp}",
        from_=TWILIO_NUMBER,
        to=f"+91{phone}"  # assuming India numbers
    )

    return otp


# otp verification 

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if entered_otp == session.get('reset_otp'):
            session['otp_verified'] = True
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('verify_otp'))

    return render_template('verify_otp.html')



# forget password 

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()

        if not user:
            flash("No account found with this email.", "error")
            return redirect(url_for('forgot_password'))

        session['reset_email'] = email
        session['reset_phone'] = user['phone']  # stored during volunteer approval

        # send OTP
        otp = send_otp(user['phone'])
        session['reset_otp'] = str(otp)

        flash("OTP sent to your registered mobile number.", "success")
        return redirect(url_for('verify_otp'))

    return render_template('forgot_password.html')



# Reset Password 

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified'):
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        email = session['reset_email']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
        conn.commit()
        conn.close()

        # clear session values
        session.pop('reset_email', None)
        session.pop('reset_phone', None)
        session.pop('reset_otp', None)
        session.pop('otp_verified', None)

        flash("Password updated successfully!", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html')







@app.route('/api/programs')
def api_programs():
    """API endpoint for programs"""
    programs_data = load_json_data('programs.json')
    return jsonify(programs_data)


@app.route('/api/programs/<program_id>')
def api_program_detail(program_id):
    """API endpoint for single program"""
    programs_data = load_json_data('programs.json')
    program = next((p for p in programs_data.get('programs', []) if p['id'] == program_id), None)
    
    if not program:
        return jsonify({'error': 'Program not found'}), 404
    
    return jsonify(program)


@app.route('/api/events')
def api_events():
    """API endpoint for events"""
    events_data = load_json_data('events.json')
    
    # Filter by status if provided
    status = request.args.get('status')
    events = events_data.get('events', [])
    
    if status:
        events = [e for e in events if e.get('status') == status]
    
    return jsonify({'events': events})


@app.route('/api/events/<event_id>')
def api_event_detail(event_id):
    """API endpoint for single event"""
    events_data = load_json_data('events.json')
    event = next((e for e in events_data.get('events', []) if e['id'] == event_id), None)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    return jsonify(event)


@app.route('/api/blog')
def api_blog():
    """API endpoint for blog posts"""
    blog_data = load_json_data('blog-posts.json')
    return jsonify(blog_data)


@app.route('/api/stats')
def api_stats():
    """API endpoint for site statistics"""
    config_data = load_json_data('config.json')
    return jsonify(config_data.get('stats', {}))


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_donations():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM donations ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()
    return rows


def save_contact_submission(name, email, phone, message):
    """Save contact form submission"""
    submission = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'name': name,
        'email': email,
        'phone': phone,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'status': 'new'
    }
    
    # Save to JSON file
    try:
        submissions_file = 'data/contact_submissions.json'
        if os.path.exists(submissions_file):
            with open(submissions_file, 'r') as f:
                data = json.load(f)
        else:
            data = {'submissions': []}
        
        data['submissions'].append(submission)
        
        with open(submissions_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        app.logger.error(f'Error saving contact submission: {str(e)}')


def save_volunteer_application(name, email, phone, city, interests, message):
    conn = get_db()
    cur = conn.cursor()

    vol_id = generate_volunteer_id()

    cur.execute("""
        INSERT INTO volunteer_applications
        (id, name, email, phone, city, interests, message, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (vol_id, name, email, phone, city, ",".join(interests),
          message, datetime.now().isoformat(), "pending"))

    conn.commit()
    return vol_id




def save_donation(amount, program, name, email, phone, is_anonymous):
    conn = get_db()
    cur = conn.cursor()

    donation_id = datetime.now().strftime('%Y%m%d%H%M%S')
    transaction_id = "TXN" + donation_id

    cur.execute("""
        INSERT INTO donations
        (donation_id, transaction_id, amount, program, donor_name, donor_email, donor_phone, is_anonymous, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        donation_id,
        transaction_id,
        amount,
        program,
        name if not is_anonymous else "Anonymous",
        email,
        phone,
        1 if is_anonymous else 0,
        datetime.now().isoformat(),
        "success"
    ))

    conn.commit()
    conn.close()

    return donation_id, transaction_id




#  Approve Volunteer 

@app.route('/admin/approve/<int:vol_id>')
def approve_volunteer(vol_id):
    if session.get('role') != 'admin':
        flash("Access denied!", "error")
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("UPDATE volunteer_applications SET status='approved' WHERE id=?", (vol_id,))
    conn.commit()
    conn.close()

    flash("Volunteer approved!", "success")
    return redirect(url_for('admin_dashboard'))



# reject / delete volunteer

@app.route('/admin/delete_volunteer/<int:vol_id>')
def delete_volunteer(vol_id):
    if session.get('role') != 'admin':
        flash("Access denied!", "error")
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM volunteer_applications WHERE id=?", (vol_id,))
    conn.commit()
    conn.close()

    flash("Volunteer deleted.", "success")
    return redirect(url_for('admin_dashboard'))



# adding manager route 

@app.route('/admin/add_manager', methods=['POST'])
def add_manager():
    if session.get('role') != 'admin':
        flash("Access denied!", "error")
        return redirect(url_for('login'))

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    file_path = 'data/users.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {'users': []}

    # prevent duplicate
    if any(u['email'] == email for u in data['users']):
        flash("Email already exists!", "error")
        return redirect(url_for('admin_dashboard'))

    new_manager = {
        "username": username,
        "email": email,
        "password": password,
        "role": "manager"
    }

    data['users'].append(new_manager)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    flash("Manager added successfully!", "success")
    return redirect(url_for('admin_dashboard'))


# Delete Users

@app.route('/admin/delete_user/<email>')
def delete_user(email):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()

    flash("User deleted.", "success")
    return redirect(url_for('admin_dashboard'))



# admin dashboard 

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Access denied!", "error")
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM volunteer_applications")
    volunteer_apps = cur.fetchall()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("SELECT * FROM donations ORDER BY id DESC")
    donations = cur.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        volunteer_apps=volunteer_apps,
        users=users,
        donations=donations
    )



# id- generator 

def generate_volunteer_id():
    year = datetime.now().year % 100          # last 2 digits of year
    file_path = 'data/volunteer_applications.json'

    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {'applications': []}

    # Count how many volunteers exist for the current year
    count = sum(1 for v in data['applications']
                if str(v['id']).startswith(str(year)))

    # new sequence
    new_seq = count + 1

    # final id: example -> 25 + 1 => 251
    return int(f"{year}{new_seq}")


def send_contact_email(name, email, phone, message):
    """Send email notification for contact form"""
    if not app.config.get('MAIL_USERNAME'):
        return
    
    msg = Message(
        subject=f'New Contact Form Submission from {name}',
        recipients=[app.config['MAIL_USERNAME']],
        body=f'''
New contact form submission:

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}
        '''
    )
    mail.send(msg)


def send_volunteer_email(name, email):
    """Send confirmation email to volunteer"""
    if not app.config.get('MAIL_USERNAME'):
        return
    
    msg = Message(
        subject='Thank you for volunteering with The Smiling Tear Foundation',
        recipients=[email],
        body=f'''
Dear {name},

Thank you for your interest in volunteering with The Smiling Tear Foundation!

We have received your application and our team will review it shortly. We will contact you within 3-5 business days with next steps.

Thank you for your commitment to making a difference!

Best regards,
The Smiling Tear Foundation Team
        '''
    )
    mail.send(msg)


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Create DB only once
    if not os.path.exists("smilingtears.db"):
        print("Database not found → Creating new SQLite database...")
        init_db()
    else:
        print("Database exists → Skipping database initialization.")

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

