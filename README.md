# AppleScout Agent with Gemini AI

This project is an automated system designed to monitor and analyze Apple-related news, social media trends, and stock market data. It generates comprehensive reports using Gemini via the `google-genai` SDK and delivers them via Telegram.

## Key Features

- AI-Powered Analysis: Utilizes Gemini for sophisticated news summarization, sentiment analysis, and insight extraction.
- Multi-Source Aggregation: Collects data from Google News, Apple Newsroom, and leading technology publications via RSS.
- Social Media Monitoring: Tracks relevant discussions on Reddit and Hacker News to gauge community sentiment.
- Market Intelligence: Integrates $AAPL stock price data and trend analysis through Stooq, Yahoo Finance Chart API, and Google Finance fallbacks.
- Risk & Opportunity Assessment: Automatically identifies potential market risks and opportunities based on collected data.
- Automated Reporting: Delivers formatted HTML reports directly to a specified Telegram chat.

## Architecture

The project adheres to a 3-layer architecture for improved reliability and maintainability:

1. Directives (Layer 1): Standard Operating Procedures (SOPs) defined in markdown files within the `directives/` directory.
2. Orchestration (Layer 2): AI-driven logic that processes directives and manages the workflow.
3. Execution (Layer 3): Deterministic Python scripts in the `execution/` folder that handle API interactions and data processing.

## Skill-Oriented Structure

The repo now includes an OpenClaw/AppleScout skill layout under `applescout/`:

- `applescout/SKILL.md`
- `applescout/scripts/`
- `applescout/prompts/`
- `applescout/references/`

The new primary entrypoint is:

```bash
python applescout/scripts/run_applescout.py
```

For validation without Telegram delivery:

```bash
python applescout/scripts/run_applescout.py --dry-run
```

Existing `execution/*.py` scripts are kept as backward-compatible wrappers.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token and Chat ID
- Google Gemini API Key

### Installation

1. Clone the repository:

   ```bash
   cd c:\appdev\apple-scout
   ```

2. Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env` and provide your credentials:

   ```bash
   copy .env.example .env
   ```

   Required variables: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GEMINI_API_KEY`.

### Telegram Configuration

1. Create a Bot: Message [@BotFather](https://t.me/botfather) on Telegram to create a new bot and obtain an API token.
2. Retrieve Chat ID: Send a message to your new bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your `chat_id`.

## Usage

### Manual Execution

To run the entire workflow manually:

```bash
python applescout/scripts/run_applescout.py
```

### Scheduled Execution

`execution/scheduler.py` is deprecated. Prefer OpenClaw cron or another external scheduler invoking:

```bash
python applescout/scripts/run_applescout.py
```

## Project Structure

- `directives/`: Legacy SOPs retained for the original architecture.
- `applescout/`: Skill-oriented docs and runnable scripts for OpenClaw use.
- `execution/`: Backward-compatible entrypoints that delegate to the skill scripts.
- `.tmp/`: Directory for intermediate data storage (auto-generated).
- `AGENTS.md`: Technical documentation on the agentic architecture.
- `README_KR.md`: Korean version of the documentation.

## Troubleshooting

- Telegram Delivery Issues: Verify that the bot token and chat ID are correct and that the bot has been initialized with a message.
- Data Collection Failures: Check network connectivity and ensure RSS feeds are accessible.
- Sentiment Analysis Errors: If using the TextBlob fallback, ensure the required corpora are downloaded:

  ```bash
  python -m textblob.download_corpora
  ```

## Cloud Deployment (GitHub Actions)

The project includes a GitHub Actions workflow for manual cloud execution. The scheduled trigger is currently disabled because local Windows Task Scheduler is the active automation path.

1. Push the code to a private GitHub repository.
2. Navigate to Settings > Secrets and variables > Actions and add your `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, and `GEMINI_API_KEY`.
3. Run the workflow manually from the GitHub Actions tab when needed.

For more details, refer to [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md).

## License

This project is licensed under the MIT License.

## 🤝 Contribution

This project follows self-annealing principles:

- Fix scripts when errors are found.
- Update `directives/` documents with new learnings.
- The system improves over time.

## 📄 License

MIT License
