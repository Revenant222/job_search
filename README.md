# Job Search Application

A comprehensive job search application designed to help users find and track job opportunities across multiple platforms.

## 🚀 Project Status

**Current Phase**: Foundation Setup  
**Version**: 0.1.0  
**Last Updated**: August 5, 2025

## 📋 Project Overview

This job search application aims to provide a unified platform for job seekers to:
- Search for jobs across multiple job boards and APIs
- Filter and sort job listings by various criteria
- Track job applications and their status
- Receive job alerts for matching opportunities
- Research companies and salary information
- Manage resumes and application materials

## 🏗️ Architecture (Planned)

### Technology Stack
- **Frontend**: To be determined (React/Vue/Angular/Streamlit)
- **Backend**: To be determined (Python/Node.js/Java/C#)
- **Database**: To be determined (PostgreSQL/MongoDB/SQLite)
- **APIs**: Job search APIs (Indeed, LinkedIn, Glassdoor, etc.)
- **Testing**: Comprehensive testing framework

### Key Features (Planned)
1. **Job Search Engine**
   - Multi-platform job search
   - Advanced filtering and sorting
   - Location-based search
   - Salary range filtering

2. **Application Tracking**
   - Track application status
   - Application history
   - Follow-up reminders
   - Interview scheduling

3. **User Management**
   - User profiles and preferences
   - Resume management
   - Skill matching
   - Job alerts

4. **Analytics & Insights**
   - Application success rates
   - Market trends
   - Salary insights
   - Company research

## 📁 Project Structure

```
job_search/
├── .cursor/                    # Project documentation and tools
│   ├── rules/                 # Development rules and guidelines
│   ├── tools/                 # Available tools and utilities
│   ├── docs/                  # Technical documentation
│   └── notes/                 # Project notes and tracking
├── config/                     # Configuration files
│   ├── settings.py            # Application settings
│   └── *_template.json        # Credential templates
├── data/                       # Data storage
│   ├── csv_source/            # Source CSV files (from Google Sheets)
│   ├── csv_output/            # Generated CSV outputs
│   ├── examples/              # Example CSV files
│   └── job_tags.json          # Job tagging data (gitignored)
├── docs/                       # User-facing documentation
│   ├── SETUP_GUIDE.md         # Setup instructions
│   ├── CSV_FORMAT_GUIDE.md    # CSV format documentation
│   └── ...                    # Other guides
├── logs/                       # Application logs
├── scripts/                    # Utility and test scripts
│   ├── batch/                 # Batch/PowerShell scripts
│   ├── tests/                 # Test scripts
│   └── utilities/             # Utility scripts
├── src/                        # Source code
│   ├── core/                  # Core functionality
│   ├── ui/                    # UI components
│   ├── utils/                 # Utility modules
│   ├── main.py                # Main entry point
│   └── streamlit_app.py       # Streamlit application
├── tests/                      # Unit tests
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── setup.py                    # Package setup
```

## 🛠️ Development Setup

### Prerequisites
- Git
- Python 3.8+ (if using Python backend)
- Node.js (if using Node.js backend)
- Database system (PostgreSQL/MongoDB/SQLite)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Revenant222/job_search.git
   cd job_search
   ```

2. Set up development environment:
   ```bash
   # Create virtual environment (Python)
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies (when requirements.txt is created)
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env with your configuration
   ```

## 📚 Documentation

### Project Documentation
- [Setup Guide](docs/SETUP_GUIDE.md) - Complete setup instructions
- [Google Service Account Setup Walkthrough](docs/GOOGLE_SERVICE_ACCOUNT_SETUP_WALKTHROUGH.md) - **Step-by-step guide with screenshots for Google Sheets integration**
- [CSV Format Guide](docs/CSV_FORMAT_GUIDE.md) - CSV file format documentation
- [Project Checklist](.cursor/notes/project_checklist.md) - Main project tracking
- [Agent Notes](.cursor/notes/agentnotes.md) - Critical session information
- [Project Notebook](.cursor/notes/notebook.md) - Research and findings
- [Versioning Rules](.cursor/rules/versioning_rules.md) - Version control guidelines

### Development Guidelines
- Follow the structured development methodology
- Create technical specifications before implementation
- Implement comprehensive testing for all features
- Keep files under 500 lines with single responsibility
- Use conventional commit messages
- Update documentation regularly

## 🔄 Development Workflow

### Git Workflow
- **Main Branch**: `main` - Production-ready code
- **Development Branch**: `dev` - Active development
- **Feature Branches**: `feature/feature-name` - Individual features

### Commit Convention
```
type(scope): description

Examples:
- feat(search): add job filtering by location
- fix(api): resolve rate limiting issue
- docs(readme): update installation instructions
```

## 🧪 Testing

### Testing Strategy
- Unit tests for individual components
- Integration tests for component interactions
- End-to-end tests for complete workflows
- API testing for external integrations

### Test Coverage
- Target: 80%+ code coverage
- All new features must include tests
- Bug fixes must include regression tests

## 🚀 Deployment

### Environment Setup
- Development environment
- Staging environment
- Production environment

### Deployment Process
1. Create release branch from `dev`
2. Update version numbers
3. Run full test suite
4. Create pull request to `main`
5. Deploy to staging for testing
6. Deploy to production

## 🤝 Contributing

### Development Process
1. Create feature branch from `dev`
2. Implement feature with tests
3. Update documentation
4. Create pull request
5. Code review and testing
6. Merge to `dev`

### Code Standards
- Follow language-specific style guides
- Write clear, documented code
- Include comprehensive tests
- Update relevant documentation

## 📈 Roadmap

### Version 0.2.0 - Basic Job Search
- [ ] Set up development environment
- [ ] Implement basic job search functionality
- [ ] Create simple user interface
- [ ] Integrate with one job API

### Version 0.3.0 - User Interface
- [ ] Design and implement UI/UX
- [ ] Add job filtering capabilities
- [ ] Implement job details view
- [ ] Add responsive design

### Version 0.4.0 - API Integrations
- [ ] Integrate multiple job APIs
- [ ] Implement data aggregation
- [ ] Add caching layer
- [ ] Handle API rate limiting

### Version 0.5.0 - Advanced Features
- [ ] Add application tracking
- [ ] Implement job alerts
- [ ] Add user authentication
- [ ] Create user profiles

### Version 1.0.0 - Production Release
- [ ] Complete testing and bug fixes
- [ ] Performance optimization
- [ ] Security audit
- [ ] Production deployment

## 📞 Support

For questions or support:
- Create an issue in the GitHub repository
- Check the project documentation
- Review the development guidelines

## 📄 License

[License information to be added]

---

**Note**: This project is in early development. Features and architecture may change as requirements are refined and development progresses. 