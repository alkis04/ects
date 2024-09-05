from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_courses():
    url = "https://www.di.uoa.gr/studies/undergraduate/courses"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    all_courses = []
    tables = soup.find_all('table', class_='table-striped')
    
    for table in tables:
        caption = table.find('caption')
        semester = caption.text.strip() if caption else "Unknown Semester"
        
        rows = table.find_all('tr')[1:]  # Skip header row
        semester_courses = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                title = cols[0].text.strip()
                code = cols[1].text.strip()
                ects = int(cols[2].text.strip())
                course_type = cols[3].text.strip()
                semester_courses.append({
                    "title": title,
                    "code": code,
                    "ects": ects,
                    "type": course_type,
                    "semester": semester,
                    "selected": False  # Adding selected flag to handle default state
                })
        
        all_courses.append({"semester": semester, "courses": semester_courses})
    
    return all_courses

@app.route('/')
def index():
    courses = scrape_courses()
    return render_template('index.html', courses=courses)

@app.route('/update_ects', methods=['POST'])
def update_ects():
    selected_courses = request.json['selectedCourses']
    total_ects = sum(course['ects'] for course in selected_courses)
    progress = min(total_ects / 240 * 100, 100)
    return jsonify({"total_ects": total_ects, "progress": progress})

if __name__ == '__main__':
    app.run(debug=True)
