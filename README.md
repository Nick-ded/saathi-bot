---

# Saathi

## Disnake Bot Cogs

## Overview

Saathi is a modular Discord bot built with **Disnake**, focused on youth mental wellness and supportive conversation.
The bot is composed of multiple cogs, each handling a specific function. Below is an overview of the available cogs and their behavior.

---

## AI Cog

The AI Cog is the core component of Saathi. It uses **Google Generative AI (Gemini)** to generate supportive, conversational responses with a mental-health focus. The bot assumes the persona of **Saathi**, a warm, non-judgmental companion designed to listen, validate feelings, and encourage healthy coping strategies.

The cog also includes moderation features such as bad word filtering, crisis-related keyword detection, and mental health resource recommendations via `mhr.json`.

### Features

* **AI Chatbot (Text-Only)**: Uses Google Generative AI (Gemini-2.0 Flash) for natural language responses.
* **Multilingual Support**: Responds in the main language used by the user (supports Hindi, English, Marathi, Tamil, Kannada, Bengali, Gujarati, Bhojpuri, and common mixed usage such as Hinglish).
* **Message Filtering**: Replaces and censors harmful or abusive words in responses.
* **Crisis / Suicide Prevention Awareness**: Detects keywords related to self-harm, suicidal ideation, intense distress, and suggests mental health resources.
* **Context Awareness**: Maintains short chat history for better contextual replies, and periodically resets to avoid unsafe identity drift.
* **Mention Handling**: Converts Discord user mentions into readable display names for the AI.
* **Resource Integration**: Uses `mhr.json` to attach country-specific mental health resources to the prompt when the message mentions a location.

### Environment Variables

The cog requires the following environment variable:

* `GEMINI_API_KEY`: Your Google Generative AI API key.

Additionally, the bot itself requires:

* `DISCORD_TOKEN`: Your Discord bot token.

These are read from the environment; they should **not** be hard-coded in the source.

### Usage

The AI Cog automatically listens to messages and responds when:

* The bot is mentioned directly.
* Certain trigger words (e.g. “depressed”, “suicide”, “anxiety”, “panic attack”, etc.) are detected in a message.
* A user replies to a message previously sent by the bot.
* The conversation occurs in DMs with the bot.

Messages starting with the configured prefix (for example `/mhr`, `/affirmation`) are treated as commands and are **not** responded to by the AI cog, so that command cogs can process them normally.

### Moderation

* Messages containing blacklisted words are filtered and censored before the response is sent.
* If a message includes a crisis-related trigger word, the AI is instructed to:

  * respond in a supportive, safe manner,
  * avoid providing any self-harm instructions,
  * encourage reaching out to trusted people or professionals,
  * where appropriate, include mental health resources based on `mhr.json`.
* The bot ignores messages starting with `^` to avoid interfering with certain manual or legacy commands.

### Configuration

* Modify the `bad_words` dictionary to add or change word filtering rules.
* Adjust the `triggers` list to change how the bot detects sensitive topics and when it should respond.
* Customize `mhr.json` to update or expand mental health resources by country.
* Modify the system prompt in `AI.py` to further tune Saathi’s conversational style and safety behavior.

### Error Handling

* If a prompt is blocked by Google’s safety systems (e.g. `BlockedPromptException`), the bot sends a generic safe response and does not crash.
* If an unexpected exception occurs (e.g. network issues, API errors), the bot logs the error to console and informs the user that an error occurred.

---

## Backup Cog

The Backup Cog allows administrators to create backups of the bot’s key files, including Python scripts, JSON configurations, and logs. The backup is automatically packaged into a `.zip` file and sent to the administrator via Discord.

### Features

* **Automated Backup**: Recursively scans the project directory and saves all `.py`, `.json`, `.yml`, and `.log` files.
* **Admin-Only Command**: Protected by `@commands.has_permissions(administrator=True)`, so only administrators can run it.
* **ZIP Archive**: The backup is packaged into a `.zip` file and sent as a Discord attachment.
* **Excludes Unnecessary Files**: Skips `.git` and related version control directories.

### Usage

* Run `^backup` (or your bot’s configured command prefix and command) in a channel where the bot has permission to send files.
* The bot will:

  * collect relevant files,
  * create a temporary backup directory,
  * zip it into `bot_backup.zip`,
  * send the zip file as an attachment,
  * clean up the temporary directory and zip afterwards.

---

## Code Cog

The Code Cog provides controlled file management capabilities for the bot, allowing users with a specific role to inspect directories and manage files within the bot’s working directory.

### Features

* **Directory Listing**: Lists the contents of a specified directory path.
* **File Reading**: Reads the contents of a specified file.
* **File Writing**: Saves provided text content to a specified file or writes an uploaded attachment to disk.
* **File Deletion**: Deletes a specified file.
* **Role-Restricted**: Only users with a specific role ID (configured in the cog) can execute these commands.

### Usage

All commands start from a base command such as:

* `^code check <directory>` – Lists the contents of the given directory.
* `^code read <file>` – Reads and displays the contents of the specified file.
* `^code write <file> <content>` – Writes the provided content into the specified file.

  * If no inline content is provided but a file is attached to the message, the attachment is saved to `<file>`.
* `^code delete <file>` – Deletes the specified file.

If output exceeds Discord’s message length limit, the cog automatically sends the data as a text file attachment instead.

---

## Journal Cog

The Journal Cog allows users to keep a simple personal journal within Discord. Entries are stored in a JSON file and can be viewed, added, or deleted by the user who created them.

### Features

* **Add Journal Entries**: Users can add journal entries with timestamps.
* **View Journal Entries**: Users can view all their own previous entries.
* **Delete Journal Entries**: Users can delete all of their entries.
* **Persistent Storage**: Journal entries are stored in `journal.json` keyed by user ID.

### Usage

* `^add_entry <entry>` – Add a journal entry containing `<entry>`.
* `^view_entries` – View all journal entries associated with the calling user.
* `^delete_entries` – Delete all journal entries for the calling user.

All entries include the UTC timestamp in ISO format and the associated text.

---

## GoodCog

The GoodCog provides simple mental health support utilities such as positive affirmations and quick access to mental health resources stored in `mhr.json`.

### Features

* **Random Affirmations**: Sends a randomly selected positive affirmation from a predefined list.
* **Mental Health Resources Lookup (`mhr`)**:

  * Uses `mhr.json` to find mental health resources for a given country.
  * Matches based on country name or any of its aliases.
  * Returns a formatted embed containing resource names and contact information.
  * Provides a generic safety footer reminding users to contact local emergency services in immediate danger.

### Usage

* `^affirmation` – Sends a random positive affirmation message to the channel.
* `^mhr <country>` – Looks up mental health resources for the specified country (e.g. `^mhr india`, `^mhr singapore`).

  * If no country is specified, a default (e.g. Singapore) may be used depending on configuration.
  * If the country is not found, the command responds with a list of available countries.

The list of affirmations as well as entries in `mhr.json` can be edited as needed.

---

## mhr.json (Mental Health Resources)

The `mhr.json` file stores mental health resources by country, including aliases for name matching and a `Data` section with key/value pairs describing helplines or websites.

### Example (India)

```json
{
  "India": {
    "Aliases": ["india", "bharat", "hindustan"],
    "Data": {
      "Aasra Helpline": "24/7 Suicide Prevention | +91 9820466726",
      "KIRAN (Govt.)": "Mental Health Helpline | 1800-599-0019",
      "ICALL (TISS Mumbai)": "Counselling Support | +91 9152987821",
      "Fortis Stress Helpline": "Dr. Samir Parikh Team | +91 8376804102",
      "Snehi Delhi": "Emotional Support | +91 9582208181"
    }
  }
}
```

You can extend this file to include other countries or additional resources as needed, following the same structure.

---

## Installation

Install the required dependencies:

```sh
pip install disnake google-generativeai pillow requests
```

Configure environment variables (`DISCORD_TOKEN`, `GEMINI_API_KEY`), then run:

```sh
python main.py
```

---
