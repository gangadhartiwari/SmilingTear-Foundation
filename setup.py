"""
Automatic Setup Script for The Smiling Tear Foundation Website
Run this script to set up the complete project structure
"""

import os
import json
import shutil
from pathlib import Path

def create_directory_structure():
    """Create all necessary directories"""
    directories = [
        'static/css',
        'static/js',
        'static/images/logo',
        'static/images/hero',
        'static/images/about',
        'static/images/programs/education',
        'static/images/programs/healthcare',
        'static/images/programs/skill-development',
        'static/images/events/2024',
        'static/images/blog/thumbnails',
        'static/images/blog/featured',
        'static/images/gallery',
        'static/images/testimonials',
        'static/videos',
        'static/documents/annual-reports',
        'static/documents/certificates',
        'static/documents/brochures',
        'static/uploads',
        'templates',
        'data',
        'logs',
    ]
    
    print("Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    print("\n✅ Directory structure created successfully!\n")


def create_env_file():
    """Create .env file with template"""
    env_content = """# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=change-this-to-a-random-secret-key

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file")
        print("  ⚠️  Please update .env with your actual credentials!")
    else:
        print("⚠️  .env file already exists, skipping...")


def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
.webassets-cache

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Uploads
static/uploads/*
!static/uploads/.gitkeep

# Database
*.db
*.sqlite

# Backups
backups/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✓ Created .gitignore file")


def create_sample_json_files():
    """Create sample JSON data files"""
    
    # config.json
    config_data = {
        "siteInfo": {
            "name": "The Smiling Tear Foundation",
            "tagline": "Empowering Lives Through Education & Healthcare",
            "description": "Dedicated to creating lasting positive change in communities across India",
            "foundedYear": 2020
        },
        "contact": {
            "email": "thesmilingtear@gmail.com",
            "phone": "+91 87003 91439",
            "address": {
                "city": "New Delhi",
                "state": "Delhi",
                "country": "India"
            }
        },
        "socialMedia": {
            "facebook": "https://facebook.com/thesmilingtear",
            "instagram": "https://instagram.com/thesmilingtear",
            "linkedin": "https://linkedin.com/company/thesmilingtear",
            "twitter": "https://twitter.com/thesmilingtear"
        },
        "stats": {
            "livesImpacted": 10000,
            "programsRunning": 50,
            "volunteers": 500,
            "partnerOrganizations": 25
        },
        "hero": {
            "title": "Transforming Lives Through",
            "highlightText": "Education & Healthcare",
            "subtitle": "Join us in making a difference. Every smile counts, every tear matters.",
            "backgroundImage": "images/hero/hero-bg-1.jpg",
            "ctaButtons": [
                {"text": "Get Involved", "link": "/volunteer", "type": "primary"},
                {"text": "Learn More", "link": "/about", "type": "secondary"}
            ]
        },
        "mission": {
            "title": "Our Mission",
            "description": "Empowering underprivileged communities through quality education, healthcare access, and sustainable development initiatives.",
            "values": [
                {
                    "icon": "fa-graduation-cap",
                    "title": "Education First",
                    "description": "Providing quality education and learning resources to children from underprivileged backgrounds.",
                    "color": "blue"
                },
                {
                    "icon": "fa-heartbeat",
                    "title": "Healthcare Access",
                    "description": "Ensuring basic healthcare services reach those who need it most.",
                    "color": "green"
                },
                {
                    "icon": "fa-hands-helping",
                    "title": "Community Development",
                    "description": "Building sustainable communities through skill development programs.",
                    "color": "yellow"
                }
            ]
        },
        "about": {
            "vision": "A world where every individual has equal access to education, healthcare, and opportunities.",
            "mission": "Empowering communities through sustainable programs in education, healthcare, and skill development.",
            "values": "Compassion, integrity, transparency, and unwavering commitment to social change.",
            "story": "The Smiling Tear Foundation was born from a simple belief: that every child deserves access to quality education and healthcare, regardless of their economic background."
        },
        "donationTiers": [
            {
                "amount": 2000,
                "title": "Education Supporter",
                "description": "Sponsors one student's education for a month",
                "icon": "fa-graduation-cap",
                "color": "blue"
            },
            {
                "amount": 5000,
                "title": "Healthcare Champion",
                "description": "Provides healthcare for 20 families",
                "icon": "fa-heartbeat",
                "color": "green",
                "popular": True
            },
            {
                "amount": 10000,
                "title": "Community Builder",
                "description": "Funds a complete skill development workshop",
                "icon": "fa-hands-helping",
                "color": "yellow"
            }
        ],
        "volunteerBenefits": [
            {
                "icon": "fa-heart",
                "title": "Make a Real Impact",
                "description": "Directly contribute to changing lives in your community",
                "color": "red"
            },
            {
                "icon": "fa-users",
                "title": "Meet Like-Minded People",
                "description": "Connect with passionate individuals who share your values",
                "color": "blue"
            },
            {
                "icon": "fa-star",
                "title": "Gain New Skills",
                "description": "Develop leadership, communication, and organizational skills",
                "color": "yellow"
            },
            {
                "icon": "fa-smile",
                "title": "Personal Fulfillment",
                "description": "Experience the joy of giving back to society",
                "color": "green"
            }
        ]
    }
    
    with open('data/config.json', 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    print("✓ Created data/config.json")
    
    # Create empty files for other data
    empty_structures = {
        'programs.json': {"programs": []},
        'events.json': {"events": []},
        'blog-posts.json': {"posts": []},
        'testimonials.json': {"testimonials": []},
        'team-members.json': {"team": []},
        'contact_submissions.json': {"submissions": []},
        'volunteer_applications.json': {"applications": []},
        'donations.json': {"donations": []}
    }
    
    for filename, structure in empty_structures.items():
        filepath = f'data/{filename}'
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(structure, f, indent=2, ensure_ascii=False)
            print(f"✓ Created data/{filename}")


def create_readme():
    """Create a simple README file"""
    readme_content = """# The Smiling Tear Foundation - Website

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Update `.env` file with your credentials

3. Add your images to the `static/images/` folders

4. Update JSON files in `data/` folder with your content

5. Run the application:
   ```
   python app.py
   ```

6. Open browser and visit: http://localhost:5000

## Need Help?

Check the complete documentation in the project files or contact: thesmilingtear@gmail.com
"""
    
    if not os.path.exists('README.md'):
        with open('README.md', 'w') as f:
            f.write(readme_content)
        print("✓ Created README.md")


def create_placeholder_files():
    """Create placeholder files"""
    # Create .gitkeep in uploads folder
    with open('static/uploads/.gitkeep', 'w') as f:
        f.write('')
    
    print("✓ Created placeholder files")


def main():
    """Main setup function"""
    print("=" * 60)
    print(" The Smiling Tear Foundation - Automatic Setup")
    print("=" * 60)
    print()
    
    # Create directory structure
    create_directory_structure()
    
    # Create configuration files
    print("Creating configuration files...")
    create_env_file()
    create_gitignore()
    create_readme()
    create_placeholder_files()
    print()
    
    # Create data files
    print("Creating data files...")
    create_sample_json_files()
    print()
    
    # Final instructions
    print("=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Update .env file with your email credentials")
    print("2. Add your images to static/images/ folders")
    print("3. Update data/config.json with your NGO information")
    print("4. Add programs, events, and blog posts to respective JSON files")
    print("5. Run: python app.py")
    print("6. Visit: http://localhost:5000")
    print()
    print("For detailed instructions, check README.md")
    print()


if __name__ == "__main__":
    main()