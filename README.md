# Automated Real Estate Agent

This project contains a simple Python script for gathering condominium
listings in Bangkok from public real estate websites. The agent scrapes
data from LivingInsider and PropertyHub, summarizes the results and can
email a weekly report.

## Setup

1. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy `config_example.json` to `config.json` and edit the SMTP and
   authentication details for sending email.

   ```bash
   cp config_example.json config.json
   # Edit config.json with your credentials
   ```

## Running

Execute the agent manually:

```bash
python real_estate_agent.py
```

You can schedule the script to run weekly using `cron` or another
scheduler of your choice.
