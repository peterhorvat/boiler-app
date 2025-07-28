# Contributing to Boiler App

Thank you for your interest in contributing to Boiler App! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/boiler-app.git
   cd boiler-app
   ```

2. **Set up development environment**
   ```bash
   cp .env.local .env
   docker-compose up -d
   ```

3. **Run initial setup**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

## 🛠️ How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/your-username/boiler-app/issues)
2. If not, create a new issue using the bug report template
3. Provide as much detail as possible, including steps to reproduce

### Suggesting Features

1. Check if the feature has already been requested
2. Create a new issue using the feature request template
3. Clearly describe the feature and its benefits

### Code Contributions

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   # Backend tests
   docker-compose exec backend python manage.py test
   
   # Frontend tests
   docker-compose exec frontend npm test
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Backend (Django)

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Use type hints where appropriate

**Example:**
```python
def create_user(email: str, password: str) -> User:
    """
    Create a new user with email and password.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        User: Created user instance
    """
    user = User.objects.create_user(
        email=email,
        password=password
    )
    return user
```

### Frontend (Vue/Nuxt)

- Use Vue 3 Composition API
- Follow [Vue Style Guide](https://vuejs.org/style-guide/)
- Use TypeScript where possible
- Use meaningful component and variable names
- Keep components small and reusable

**Example:**
```vue
<template>
  <div class="user-card">
    <h3>{{ user.name }}</h3>
    <p>{{ user.email }}</p>
  </div>
</template>

<script setup lang="ts">
interface User {
  id: number
  name: string
  email: string
}

defineProps<{
  user: User
}>()
</script>
```

### CSS/Styling

- Use Tailwind CSS classes
- Follow mobile-first approach
- Use semantic class names for custom CSS
- Avoid inline styles

## 📋 Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```bash
feat: add user authentication
fix: resolve login form validation issue
docs: update API documentation
style: format code according to PEP 8
refactor: extract user service logic
test: add unit tests for user model
chore: update dependencies
```

## 🔄 Pull Request Process

1. **Before submitting:**
   - Ensure all tests pass
   - Update documentation if needed
   - Follow the coding standards
   - Rebase your branch on the latest main

2. **PR Requirements:**
   - Use the PR template
   - Provide clear description of changes
   - Link related issues
   - Add screenshots for UI changes
   - Ensure CI/CD pipeline passes

3. **Review Process:**
   - At least one reviewer approval required
   - Address all review comments
   - Keep PR scope focused and small
   - Squash commits before merging

## 🧪 Testing

### Backend Testing

```bash
# Run all tests
docker-compose exec backend python manage.py test

# Run specific test
docker-compose exec backend python manage.py test apps.users.tests.test_models

# Run with coverage
docker-compose exec backend coverage run --source='.' manage.py test
docker-compose exec backend coverage report
```

### Frontend Testing

```bash
# Run unit tests
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec frontend npm run test:coverage

# Run e2e tests
docker-compose exec frontend npm run test:e2e
```

### Writing Tests

#### Backend Tests
```python
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        """Test creating a user with email."""
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(
            email=email,
            password=password
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
```

#### Frontend Tests
```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UserCard from '~/components/UserCard.vue'

describe('UserCard', () => {
  it('displays user information', () => {
    const user = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com'
    }
    
    const wrapper = mount(UserCard, {
      props: { user }
    })
    
    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@example.com')
  })
})
```

## 📚 Documentation

- Update README.md for significant changes
- Add inline code comments for complex logic
- Update API documentation for backend changes
- Add JSDoc comments for complex functions

## 🆘 Getting Help

- Check existing [Issues](https://github.com/your-username/boiler-app/issues)
- Join our [Discussions](https://github.com/your-username/boiler-app/discussions)
- Contact maintainers directly

## 📄 License

By contributing to Boiler App, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Boiler App! 🚀