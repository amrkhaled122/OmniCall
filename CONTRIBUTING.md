# Contributing to OmniCall

Thank you for considering contributing to OmniCall! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](../../issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Your environment (OS, Python version, etc.)

### Suggesting Features

1. Check if the feature has been requested in [Issues](../../issues)
2. Create a new issue with:
   - Clear description of the feature
   - Why it would be useful
   - How it should work
   - Any examples or mockups

### Code Contributions

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/OmniCall.git
   cd OmniCall
   ```

3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**:
   - Follow the existing code style
   - Add comments where needed
   - Test your changes thoroughly

5. **Commit** your changes:
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Wait for review

## Development Setup

### Requirements

- Python 3.11+
- Node.js 18+
- Firebase account (for Cloud Functions)

### Setup Steps

1. **Install Python dependencies**:
   ```bash
   pip install -r pc_app/requirements.txt
   ```

2. **Install Node dependencies** (for Cloud Functions):
   ```bash
   cd functions
   npm install
   cd ..
   ```

3. **Run the app**:
   ```bash
   python pc_app/omnicall_app.py
   ```

## Code Style

### Python
- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Add docstrings to functions
- Keep functions focused and small

### JavaScript
- Use ES6+ features
- Use `const` and `let` (no `var`)
- Add JSDoc comments for functions
- Handle errors properly

### General
- Write clear, self-documenting code
- Add comments for complex logic
- Keep commits atomic and well-described

## Testing

Before submitting a PR:

1. **Test all features**:
   - Registration
   - Pairing
   - Notifications
   - Statistics
   - Feedback submission

2. **Test on clean install**:
   - Remove `%APPDATA%/OmniCall`
   - Run fresh registration

3. **Check for errors**:
   - No console errors
   - No unhandled exceptions
   - Proper error messages

## Pull Request Guidelines

### PR Title Format
- `Add: [description]` - New feature
- `Fix: [description]` - Bug fix
- `Update: [description]` - Update existing feature
- `Refactor: [description]` - Code refactoring
- `Docs: [description]` - Documentation only

### PR Description
Include:
- What changes were made
- Why they were made
- How to test them
- Screenshots (if UI changes)
- Related issues (if any)

### Checklist
- [ ] Code follows project style
- [ ] Changes have been tested
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or documented)
- [ ] Commits are clean and descriptive

## Questions?

Feel free to:
- Open an issue for discussion
- Email: amrkhaled122@aucegypt.edu
- Start a discussion in [Discussions](../../discussions)

## Code of Conduct

Be respectful and constructive:
- Be welcoming to newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

Thank you for contributing! 🚀
