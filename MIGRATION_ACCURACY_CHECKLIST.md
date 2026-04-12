# Django to Flask Migration Accuracy Checklist

## 1. Pre-Migration Preparation
- [ ] Backup original Django project
- [ ] List all Django apps, models, views, forms, templates, urls
- [ ] Identify custom middleware, signals, decorators, and third-party packages

## 2. Automated Conversion
- [ ] Run initial automated conversion (custom scripts or tools)
- [ ] Ensure all files are generated in Flask structure

## 3. Component-Specific Accuracy Improvers
- [ ] Run accuracy improvers for:
    - [ ] Models (SQLAlchemy patterns, relationships)
    - [ ] Views/Routes (Flask patterns, request handling)
    - [ ] Templates (Jinja2 syntax, inheritance)
    - [ ] URLs (Flask blueprints/routes)
    - [ ] Forms/Queries (Flask-WTF, query logic)

## 4. AI-Driven Enhancement
- [ ] Use AIProjectEnhancer to process every .py file
    - [ ] Ensure correct provider/model is set (Gemini, OpenAI, Claude)
    - [ ] Review per-file accuracy scores and improvements
- [ ] Re-run AI enhancement on files with low scores (<80%)

## 5. Comprehensive Validation
- [ ] Run AIProjectValidator on the entire Flask project
    - [ ] Check for syntax errors in all files
    - [ ] Validate Flask/SQLAlchemy imports
    - [ ] Ensure no Django patterns remain
    - [ ] Confirm Flask app structure and blueprints
    - [ ] Validate authentication and database setup

## 6. Manual Review
- [ ] Manually inspect files flagged by validator or with low AI scores
- [ ] Pay special attention to:
    - [ ] Custom middleware/decorators
    - [ ] Complex ORM logic
    - [ ] Template context and inheritance

## 7. Testing
- [ ] Write and run unit/integration tests for all major routes and models
- [ ] Use Flask test client to simulate requests and validate responses
- [ ] Fix any failing tests and re-validate

## 8. Finalization
- [ ] Remove any unused or legacy Django files
- [ ] Update documentation and requirements.txt
- [ ] Deploy and test in staging/production environment

---

**Tip:** Repeat steps 4-7 as needed until all validation and tests pass with high accuracy.
