# Search MCP

**Tool Pattern:** `mcp__search__*`

## Purpose
Semantic and advanced search across documentation and code.

## Primary Commands

- `search__semantic` - Find conceptually related content
- `search__fuzzy` - Search with typo tolerance
- `search__index` - Build searchable index
- `search__query` - Advanced query with filters
- `search__similar` - Find similar documents

## When to Use

- Answering knowledge base queries
- Finding related documentation
- Searching with fuzzy matching
- Building documentation indexes
- Discovering similar content

## Fallback

Standard Grep tool with regex patterns

## Example Usage

```
# Check for MCP
[Look for mcp__search__semantic]

# With MCP
mcp__search__semantic query="authentication patterns"

# Without MCP (fallback)
Grep pattern="authentication.*pattern" output_mode="content"
```

## Benefits

- Semantic understanding
- Typo tolerance
- Better relevance ranking
- Cross-document relationships
- Faster indexed search
