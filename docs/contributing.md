# Contributing to SecureScout

Thank you for your interest in contributing to SecureScout! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Environment](#development-environment)
4. [Coding Standards](#coding-standards)
5. [Git Workflow](#git-workflow)
6. [Pull Request Process](#pull-request-process)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation](#documentation)
9. [Security Considerations](#security-considerations)
10. [License](#license)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) file for details.

## Getting Started

### Issues

Before starting work on a new feature or bug fix, please check the [issue tracker](https://github.com/aegntic/sec-scout/issues) to see if the task is already being worked on. If not, create a new issue to discuss the proposed changes.

Good issues to start with are labeled `good-first-issue` or `help-wanted`.

### Feature Requests

For feature requests, please create an issue with the `enhancement` label. Provide as much context as possible, including:

- A clear description of the feature
- Use cases for the feature
- Any potential implementation details
- How the feature contributes to the project's goals

## Development Environment

### Setting Up a Development Environment

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/sec-scout.git
   cd sec-scout
   ```

3. Set up the upstream remote:
   ```bash
   git remote add upstream https://github.com/aegntic/sec-scout.git
   ```

4. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. Set up frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Running the Development Environment

We recommend using the provided Docker development environment:

```bash
docker-compose -f docker-compose.dev.yml up
```

Alternatively, you can run the backend and frontend separately:

```bash
# Backend
python -m backend.app

# Frontend (in another terminal)
cd frontend
npm start
```

## Coding Standards

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Keep lines under 100 characters
- Use meaningful variable and function names

### JavaScript/React Code

- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use ESLint with our provided configuration
- Use functional components and hooks for React
- Use PropTypes for component props
- Keep component files small and focused on a single responsibility

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add XSS scanning module for JavaScript contexts

- Implements dynamic JavaScript context analysis
- Adds payload generation for DOM-based XSS
- Includes detection for both reflected and stored XSS
- Adds automated tests for the module

Fixes #123
```

## Git Workflow

We use a simplified Git workflow:

1. Create a new branch for each feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes, with regular commits following our commit message guidelines

3. Keep your branch updated with upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a pull request with a clear title and description

## Pull Request Process

1. Ensure your code follows our coding standards
2. Update documentation if necessary
3. Add or update tests for your changes
4. Ensure all tests pass
5. Submit your pull request with a descriptive title and detailed description
6. Wait for a review from the maintainers
7. Address any requested changes
8. Once approved, a maintainer will merge your PR

## Testing Guidelines

We use pytest for Python testing and Jest for JavaScript testing.

### Python Tests

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a PR:
  ```bash
  pytest
  ```
- Use mocks and fixtures where appropriate
- Include test edge cases
- Test for both success and failure conditions

### JavaScript Tests

- Write unit tests for all React components
- Test both component rendering and behavior
- Run tests before submitting a PR:
  ```bash
  cd frontend
  npm test
  ```

## Documentation

Documentation is a crucial part of the project:

- Update the README.md if you change core functionality
- Document all new features in the appropriate docs/ files
- Update API documentation if you change any endpoints
- Add JSDoc comments to JavaScript functions
- Update the user guide for any user-facing changes

## Security Considerations

Security is a primary concern for SecureScout:

- Never commit credentials or secrets
- Use parameterized queries for database operations
- Sanitize all user inputs
- Follow secure coding practices (OWASP guidelines)
- Report security vulnerabilities privately to the maintainers
- Conduct security reviews for your own code before submitting

### Reporting Security Issues

If you discover a security vulnerability, please do NOT open an issue. Email security@example.com instead.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).