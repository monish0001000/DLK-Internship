# 🤝 Contributing to SentinelX

First off, thank you for considering contributing to SentinelX EDR! 

We welcome contributions from the community, whether it's adding new detection rules, fixing bugs, or improving documentation.

## How to Contribute

1. **Fork the Repository**: Start by forking the project to your own GitHub account.
2. **Clone Locally**: 
   ```bash
   git clone https://github.com/your-username/SentinelX-EDR.git
   ```
3. **Create a Feature Branch**: Use a descriptive name for your branch.
   ```bash
   git checkout -b feature/AddAwesomeDetectionRule
   ```
4. **Make Your Changes**: Write clean, self-documenting code. Ensure you add or update tests if applicable.
5. **Commit Your Changes**: Use clear and meaningful commit messages.
   ```bash
   git commit -m "feat: Add new Sigma rule for LSASS dumping"
   ```
6. **Push to Your Fork**:
   ```bash
   git push origin feature/AddAwesomeDetectionRule
   ```
7. **Submit a Pull Request**: Go to the original SentinelX repository and open a Pull Request. Provide a detailed description of your changes.

## Code Standards

- **Python (Backend)**: We use `flake8` and `black` for formatting. Please ensure your code conforms to PEP 8 standards.
- **React (Frontend)**: Follow React hooks best practices. Use Tailwind CSS for styling rather than custom CSS files.
- **Documentation**: If you add a new feature, please update the relevant documentation (`API.md`, `README.md`, etc.).

## Reporting Bugs

If you find a bug, please open an issue with:
- A clear and descriptive title.
- Steps to reproduce the bug.
- Expected vs actual behavior.
- Relevant logs or screenshots.

Thank you for helping make SentinelX better!
