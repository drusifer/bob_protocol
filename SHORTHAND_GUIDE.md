# Shorthand Guide for Persona Services

To make interacting with the Persona-as-a-Service (PaaS) system faster, you can use the following shorthand prefixes. When you use these aliases, the system will expand them into the full MCP service commands.

## Shorthand Convention

The convention is to use a short, intuitive alias for the persona, followed by the command and its parameters.

`shorthand <command> [parameters...]`

### Example
Typing this:
`morph plan "Create a new TUI screen for diagnostics."`

Is equivalent to executing this:
`mcp__morpheus__plan goal="Create a new TUI screen for diagnostics."`

## Alias Reference Table

| Persona | **Shorthand** | Example Usage | Expanded Command |
| :--- | :--- | :--- | :--- |
| Morpheus | `morph` | `morph plan "New UI"` | `mcp__morpheus__plan goal="New UI"` |
| Neo | `neo` | `neo implement "US-123"` | `mcp__neo__implement story="US-123"` |
| Trin | `trin` | `trin verify "US-123"` | `mcp__trin__verify feature="US-123"` |
| Oracle | `ora` | `ora ask "What is the pattern?"` | `mcp__oracle__ask question="..."` |
| Cypher | `cy` | `cy define "New login flow"` | `mcp__cypher__define_feature request="..."` |
| Mouse | `mouse` | `mouse status` | `mcp__mouse__status` |
| Bob | `bob` | `bob reprompt "neo"` | `mcp__bob__reprompt service="neo"` |

---

Feel free to use these shorthands in all your future requests.
