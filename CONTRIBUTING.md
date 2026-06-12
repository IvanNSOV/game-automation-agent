# Contributing to Autonomous Gameplay Agent

We welcome contributions! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on educational and legal use cases only
- No contributions for online multiplayer exploitation

## Getting Started

### Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/game-automation-agent.git
cd game-automation-agent
git checkout -b feature/your-feature-name
```

### Setup Development Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

## Development Workflow

### 1. Write Tests First (TDD)
```bash
# Write test in tests/test_*.py
pytest tests/test_your_feature.py -v
```

### 2. Implement Feature
```bash
# Code in src/
```

### 3. Format Code
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

### 4. Run All Tests
```bash
pytest tests/ -v --cov=src/
```

### 5. Commit and Push
```bash
git add .
git commit -m "Add feature: descriptive message"
git push origin feature/your-feature-name
```

### 6. Create Pull Request
- Go to GitHub and create a PR
- Describe what your feature does
- Reference any related issues

## Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use type hints for function signatures
- Maximum line length: 100 characters

### Example:
```python
from typing import List, Tuple, Optional

def calculate_distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float],
) -> float:
    """Calculate Euclidean distance between two points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
    
    Returns:
        Euclidean distance
    """
    import math
    return math.sqrt(
        (point1[0] - point2[0]) ** 2 +
        (point1[1] - point2[1]) ** 2
    )
```

### Docstring Format
- Use Google-style docstrings
- Include type hints in comments if Python < 3.9
- Document all public methods

## Adding Tests

### Test File Structure
```python
"""Unit tests for [module]."""

import pytest
from src.module import YourClass


class TestYourClass:
    """Test YourClass."""
    
    @pytest.fixture
    def instance(self):
        """Fixture for class instance."""
        return YourClass()
    
    def test_feature(self, instance):
        """Test specific feature."""
        result = instance.method()
        assert result == expected_value
```

### Run Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_detection.py

# Specific test class
pytest tests/test_detection.py::TestYOLOv8Detector

# Specific test method
pytest tests/test_detection.py::TestYOLOv8Detector::test_initialization

# With coverage
pytest --cov=src/ --cov-report=html
```

## Issues and Bug Reports

### Before Creating an Issue
1. Check existing issues
2. Test with latest main branch
3. Include:
   - OS and Python version
   - Error message and traceback
   - Steps to reproduce
   - config.yaml (with sensitive info removed)

### Issue Title Format
```
[BUG] Description of issue
[FEATURE] Description of feature request
[QUESTION] Your question
```

## Pull Request Process

1. **Update**: Ensure your fork is up to date with main
2. **Test**: All tests must pass: `pytest tests/`
3. **Format**: Code must be formatted: `black src/ tests/`
4. **Type Check**: No type errors: `mypy src/`
5. **Document**: Update docs if needed
6. **Sign Off**: Agree to contributing guidelines

### PR Title Format
```
[FEATURE] Short description
[FIX] Short description
[DOCS] Short description
[REFACTOR] Short description
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue with [QUESTION] tag or contact maintainers.

Thank you for contributing! 🎉
