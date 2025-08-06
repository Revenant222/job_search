# Versioning Rules for Job Search Project

## Version Control Strategy

### Git Workflow
- **Main Branch**: `main` - Production-ready code
- **Development Branch**: `dev` - Active development
- **Feature Branches**: `feature/feature-name` - Individual features
- **Hotfix Branches**: `hotfix/issue-description` - Critical bug fixes

### Commit Message Format
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
- `feat(search): add job filtering by location`
- `fix(api): resolve rate limiting issue with Indeed API`
- `docs(readme): update installation instructions`

### Branch Naming Conventions
- Feature branches: `feature/descriptive-name`
- Bug fixes: `fix/issue-description`
- Hotfixes: `hotfix/critical-issue`
- Documentation: `docs/topic`

### Version Numbering
Follow Semantic Versioning (SemVer):
- **Major.Minor.Patch**
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

### Release Process
1. Create release branch from `dev`
2. Update version numbers
3. Update changelog
4. Create pull request to `main`
5. Tag release with version number
6. Merge to `main`
7. Deploy to production

### File Versioning
- Keep version numbers in `package.json` (if applicable)
- Maintain `CHANGELOG.md` for release notes
- Use version tags in Git for releases
- Document breaking changes clearly

### Backup Strategy
- Push to remote repository at least once per hour during active development
- Create tagged releases at significant milestones
- Maintain backup of critical configuration files
- Document recovery procedures in `agentnotes.md`

## Project-Specific Versioning

### Job Search Application
- **Current Version**: 0.1.0 (Initial setup)
- **Target Version**: 1.0.0 (MVP release)
- **Development Phase**: Foundation

### Version Milestones
- **0.1.0**: Project setup and documentation
- **0.2.0**: Basic job search functionality
- **0.3.0**: User interface implementation
- **0.4.0**: API integrations
- **0.5.0**: Advanced features (filtering, sorting)
- **0.6.0**: Testing and bug fixes
- **0.7.0**: Performance optimization
- **0.8.0**: User authentication and profiles
- **0.9.0**: Final testing and polish
- **1.0.0**: Production release

### Configuration Files
- `requirements.txt` (Python dependencies)
- `package.json` (Node.js dependencies, if applicable)
- `.env.example` (Environment variables template)
- `docker-compose.yml` (Container configuration, if applicable)

### Documentation Versioning
- Update version numbers in documentation files
- Maintain version history in `CHANGELOG.md`
- Tag documentation releases with code releases
- Keep API documentation versioned separately if needed 