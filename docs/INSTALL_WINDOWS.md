# Windows Install Notes

Project Copilot v0.3 Alpha currently supports the official one-command installer on macOS, Linux, and WSL.

## Recommended Today

Use Windows Subsystem for Linux:

```bash
curl -LsSf https://raw.githubusercontent.com/Yingxing-AI/project-copilot/main/install.sh | sh
```

Then verify:

```bash
project-copilot --version
project-copilot doctor
```

## Native PowerShell

Native Windows PowerShell installation is not packaged yet.

Planned support:

- A PowerShell install script.
- Clear PATH setup guidance.
- A Windows-specific doctor check.

Until then, WSL is the recommended Windows path.
