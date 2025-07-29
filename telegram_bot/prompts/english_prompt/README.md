# Prompt Files

This folder contains the markdown files that define the system prompts for the Cupid Yukio Matchmaker Bot.

## File Structure

### Core Prompt Files
- **`role.md`** - Defines the bot's identity as Cupid Yukio, an advanced AI matchmaker
- **`object.md`** - Outlines the primary objectives for facilitating successful matches
- **`skill.md`** - Lists the bot's expertise areas and capabilities
- **`constraint.md`** - Establishes safety, privacy, and ethical guidelines
- **`workflow.md`** - Provides a structured 4-phase approach for interactions

### Gender-Specific Files
- **`male.md`** - Tailored guidance for male users
- **`female.md`** - Tailored guidance for female users
- **`neutral.md`** - Universal guidance for neutral/other users

## How It Works

The MatchmakerBot reads these files dynamically and combines them to create the complete system prompt. The gender-specific file is selected based on the user's gender preference:

- Male users → `male.md` is included
- Female users → `female.md` is included
- Neutral/Other users → `neutral.md` is included

## Customization

You can modify any of these files to customize the bot's behavior:

1. **Edit core prompts** to change the bot's fundamental approach
2. **Modify gender-specific files** to adjust advice for different user groups
3. **Add new sections** by creating additional markdown files and updating the bot code

## File Format

Each file should:
- Use markdown formatting
- Have a clear heading (e.g., `# ROLE`)
- Contain relevant content for that section
- Be written in a clear, professional tone

## Example Structure

```markdown
# SECTION NAME

Content for this section goes here.

- Bullet points for lists
- More bullet points

Additional content as needed.
``` 