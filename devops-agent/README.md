# Terraform DevOps Agent Workspace

This directory packages the Terraform Agentic Orchestrator backend (FastAPI + Microsoft Agent Framework) together with a CopilotKit/Next.js UI following the [AG-UI reference project](https://github.com/ag-ui-protocol/ag-ui). Running `npm run dev` from here starts both the coworker UI and the FastAPI server so you can exercise the workflow end-to-end without juggling multiple repositories.

## Prerequisites

- OpenAI or Azure OpenAI credentials (for the Microsoft Agent Framework agent)
- Python 3.12+
- uv
- Node.js 20+ 
- Any of the following package managers:
  - pnpm (recommended)
  - npm
  - yarn
  - bun

> **Note:** This repository ignores lock files (package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb) to avoid conflicts between different package managers. Each developer should generate their own lock file using their preferred package manager. After that, make sure to delete it from the .gitignore.

## Getting Started

1. Install dependencies using your preferred package manager:

   ```bash
   # Using pnpm (recommended)
   pnpm install

   # Using npm
   npm install

   # Using yarn
   yarn install

   # Using bun
   bun install
   ```

   > **Note:** This automatically sets up the Python environment as well.
   >
   > If you have manual issues, you can run:
   >
   > ```sh
   > npm run install:agent
   > ```

2. Copy `agent/.env.example` to `agent/.env` and fill in the environment variables described in the root `README.md` (OSS/OpenAI endpoints, Codex credentials, Terraform paths, GitHub tokens, etc.). This file lives alongside the FastAPI code so `uv run` picks it up automatically.

3. Start the development server:

   ```bash
   # Using pnpm
   pnpm dev

   # Using npm
   npm run dev

   # Using yarn
   yarn dev

   # Using bun
   bun run dev
   ```

   This will start both the UI and the Microsoft Agent Framework server concurrently.

## Available Scripts

The following scripts can also be run using your preferred package manager:

- `dev` – Starts both UI and agent servers in development mode
- `dev:debug` – Starts development servers with debug logging enabled
- `dev:ui` – Starts only the Next.js UI server
- `dev:agent` – Starts only the Microsoft Agent Framework server
- `build` – Builds the Next.js application for production
- `start` – Starts the production server
- `lint` – Runs ESLint for code linting
- `install:agent` – Installs Python dependencies for the agent

## Documentation

The main UI component is in `src/app/page.tsx`. You can:

- Modify the theme colors and styling
- Add new frontend actions
- Customize the CopilotKit sidebar appearance

## 📚 Documentation

- [Microsoft Agent Framework](https://aka.ms/agent-framework) – Learn more about Microsoft Agent Framework and its features
- [CopilotKit Documentation](https://docs.copilotkit.ai) – Explore CopilotKit’s capabilities
- [Next.js Documentation](https://nextjs.org/docs) – Learn about Next.js features and API

## Contributing

Feel free to submit issues and enhancement requests! This starter is designed to be easily extensible.

## License

This project is licensed under the MIT License – see the LICENSE file for details.

## Troubleshooting

### Agent Connection Issues

If you see "I'm having trouble connecting to my tools", make sure:

1. The Microsoft Agent Framework agent is running on port 8000
2. Your OpenAI/Azure credentials are set correctly
3. Both servers started successfully

### Python Dependencies

If you encounter Python import errors:

```bash
cd agent
uv sync
uv run src/main.py
```
