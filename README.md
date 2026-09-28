# MapLeads Pro 🚀

## Google Maps Multi-Service & Multi-Location Lead Generation Engine

**MapLeads Pro** is a web-based lead generation and business research tool designed to automate Google Maps business searches across multiple services and locations.

Instead of manually searching Google Maps for every service and city, users can enter multiple services and locations. MapLeads Pro automatically creates the required **service × location combinations**, runs the searches, processes business profiles, collects available business information, provides filtering options, and exports results to Excel.

---

## ✨ Features

### 🔎 Multi-Service & Multi-Location Search

Enter multiple services and locations in a single job.

For example:

**Services**

- Plumbers
- Electricians
- Roofers

**Locations**

- New York
- Chicago
- Houston

MapLeads Pro automatically creates combinations such as:

```text
Plumbers × New York
Plumbers × Chicago
Plumbers × Houston

Electricians × New York
Electricians × Chicago
Electricians × Houston

Roofers × New York
Roofers × Chicago
Roofers × Houston

This allows multiple searches to be managed through a single workflow.

**📊 Configurable Search Limits
**
Users can choose how many businesses to process for each search.

Available options include:

5 — Fast Test
10
25 — Recommended
50
100
200
500
1000 — Maximum
Custom

This allows users to perform small tests as well as larger lead-generation searches.

**🔄 Search Controls
**
The dashboard provides controls for managing the automation process:

▶️ Start
⏸️ Pause
▶️ Resume
⏹️ Stop
📈 Live Automation Progress

The dashboard provides live information about the current search job.

**Users can monitor:
**
Overall job completion
Search queue
Total search combinations
Current search
Total businesses found
Profiles processed
Remaining businesses
Active target
Current extraction status
🧹 Duplicate Management

MapLeads Pro provides options for handling duplicate businesses.

**Available options include:
**
Remove & Merge
Keep All

This helps keep exported lead data organized and reduces unnecessary duplicate records.

**🎯 Lead Filtering
**
Collected business records can be filtered from the dashboard.

Service

Filter businesses according to the searched service or category.

Location

Filter businesses according to the searched location.

Google Maps Claim Status

Filter results by claim status:

Claim Available
Claim Not Available
Unknown
Email Availability

Filter results according to available email information:

Has Email
No Email
📥 Excel Export

Collected business data can be exported to:

.xlsx

The exported data can be opened using Microsoft Excel and processed further with Python/OpenPyXL.

This can be useful for:

Lead generation
Sales prospecting
Local SEO prospecting
Market research
Business research
Outreach preparation
CRM preparation

**🖥️ Dashboard
**
MapLeads Pro provides a web-based dashboard for managing searches and reviewing collected businesses.

The dashboard includes three primary areas.

**1. Search Inputs & Combination Matrix
**
Users can enter:

Multiple services
Multiple locations
Maximum businesses per search
Duplicate-handling preference

The application then creates the service × location search matrix.

**2. Live Automation Progress
**
The progress section allows users to monitor the current job.

It displays information such as:

Overall Completion
Search Queue
Current Search
Total Found
Profiles Processed
Remaining
Active Target
Extraction Status

**3. Collected Businesses & Leads
**
Collected businesses are displayed in the results section.

Users can:

Review collected businesses
Filter results
Filter by service
Filter by location
Filter by email availability
Filter by claim status
Export results to Excel
🔄 How MapLeads Pro Works
Enter Services
       ↓
Enter Locations
       ↓
Generate Service × Location Combinations
       ↓
Configure Search Limit
       ↓
Start Search
       ↓
Search Google Maps
       ↓
Process Business Profiles
       ↓
Collect Available Business Information
       ↓
Handle Duplicate Records
       ↓
Filter Results
       ↓
Export Results to Excel
💡 Example Use Case

A digital marketing agency wants to find potential local business prospects in several cities.

The agency could enter:

Services
Dentists
Chiropractors
Lawyers
Locations
Dallas
Austin
Houston

MapLeads Pro generates the required combinations:

Dentists × Dallas
Dentists × Austin
Dentists × Houston

Chiropractors × Dallas
Chiropractors × Austin
Chiropractors × Houston

Lawyers × Dallas
Lawyers × Austin
Lawyers × Houston

The searches can then be processed through the application.

After the search is completed, the collected businesses can be reviewed, filtered, and exported to Excel for further research or business workflows.

**🛠️ Technology Stack
**
MapLeads Pro uses technologies including:

Python
Flask
HTML
CSS
JavaScript
OpenPyXL
Browser Automation
Web Data Extraction


**📦 Installation
Requirements**

Before running MapLeads Pro, make sure you have:

Windows, macOS, or Linux
Python 3.x
pip

A supported web browser
**🪟 Windows CMD Running Guide
**
This guide explains how to clone and run MapLeads Pro using Windows Command Prompt.

** Install Python
**
Install Python 3.x on your computer.

During installation, make sure the following option is enabled:

Add Python to PATH

After installation, open Command Prompt and run:

python --version

You should see a result similar to:

Python 3.x.x

Check pip:

pip --version

** Clone the Repository
**
Open Command Prompt.

Move to the location where you want to store the project.

For example:

cd Desktop


**Start the application with:
**
python server.py

If the server starts successfully, it should display a local address.

For example:

http://127.0.0.1:5000

Open the displayed address in your web browser.

For example:

http://127.0.0.1:5000

The MapLeads Pro dashboard should then open.

**⏹️ Stopping the Application
**
To stop the running server, return to the Command Prompt window and press:

CTRL + C

The local server will stop.

**🔁 Running MapLeads Pro Again
**
After the project has already been installed, you only need to activate the virtual environment and start the server again.

Open CMD and navigate to the project directory:

cd path\to\GoogleMapLeadGen

Activate the virtual environment:

venv\Scripts\activate

Start the application:

python server.py

Then open the local address shown in the terminal.

**🧪 Quick Test
**
For the first test, use a small search instead of a large job.

Example:

Service:
Plumber

Location:
New York

Businesses per search:
5

**Start the search and verify that:
**
The search starts successfully
The progress information updates
Businesses appear in the results
Filters work correctly
The results can be exported to Excel

After the small test works correctly, larger searches can be performed.

**📁 Project Structure
**
The main project structure is:

GoogleMapLeadGen/
│
├── .agents/
│
├── static/
│
├── templates/
│
├── excel_exporter.py
├── scraper_engine.py
├── server.py
├── verify_pipeline.py
│
├── GEMINI.md
├── MASTER_COMMAND.md
├── meta-tags-boilerplate.html
├── schema-local-business.json
│
└── verified_export.xlsx

**📂 Main Project Files
**
server.py

Main application/server entry point.

It handles the web application and connects the different components of the system.

scraper_engine.py

Contains the search and business data extraction functionality.

excel_exporter.py

Handles exporting collected business information to Excel.

verify_pipeline.py

Used for testing and verifying parts of the processing pipeline.

templates/

Contains the HTML templates used by the web application.

static/

Contains frontend resources such as CSS, JavaScript, and other static assets.

schema-local-business.json

Contains the local-business data schema used by the project.

meta-tags-boilerplate.html

Contains reusable HTML/meta-tag content.

GEMINI.md

Project documentation/instructions related to the development workflow.

MASTER_COMMAND.md

Contains project-level commands or development instructions.

verified_export.xlsx

Example/generated Excel output from the data-processing workflow.



**📊 Potential Use Cases
**
MapLeads Pro can be used for:

Local SEO prospecting
Digital marketing research
Lead generation
Sales prospecting
Local business research
Market research
Competitor research
Business data research
Outreach preparation
CRM data preparation
**⚠️ Responsible Use
**
MapLeads Pro is intended for legitimate business research and lead-generation workflows.

Users are responsible for complying with applicable laws, privacy requirements, website terms, and data-protection requirements when using the software.

Use the tool responsibly and do not collect, process, or distribute personal information unlawfully.

**🚧 Project Status
**System Ready

Current functionality includes:

✅ Multi-service searches
✅ Multi-location searches
✅ Service × location combinations
✅ Configurable search limits
✅ Start / Pause / Resume / Stop controls
✅ Live progress tracking
✅ Duplicate handling
✅ Lead filtering
✅ Email availability filtering
✅ Claim-status filtering
✅ Excel export
🔮 Future Improvements

Planned or possible future improvements include:

Advanced lead scoring
Automated lead qualification
CRM integrations
Additional export formats
Advanced analytics
Scheduled searches
Additional filtering options
Improved duplicate detection
Additional business-data fields
More automation controls
**👨‍💻 Author
****Misbah Ur Rehman Saim
**
Digital Marketing & SEO Specialist

GitHub

https://github.com/misbahurrehmansaim

LinkedIn

https://www.linkedin.com/in/misbahurrehmansaim

**⭐ Support
**
If you find MapLeads Pro useful, consider giving the repository a ⭐ on GitHub.

Suggestions, improvements, and contributions are welcome.
