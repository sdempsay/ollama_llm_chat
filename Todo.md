# TODO Items
## System prompts
- [ ] Add System prompts to the database
- [ ] Add Dialog to create and edit system prompts
- [ ] Fix population of System Prompt dropdown

## Ollama modular
- [ ] Move the Ollama code into its own library

## SQL modular
- [ ] Move SQL interactions into its own library

## Chat sidebar
- [x] Fix chat deletion
- [x] Add chat rename
- [ ] Add chat tag support
- [ ] Group chats into either tags or creation dates
- [ ] Add dialog for new Chat that includes a name, tag, and system prompt and possibly a context statement
- [ ] Make system prompt a fixed value at chat creation

## Main chat area
- [ ] add the ability to compare 2 LLM responses for the same prompt, choosing which to save to move on

## Additional features
- [ ] Add RAG support
- [ ] Determine if SQL can vector a chat session to refer to by tag as a RAG
- [ ] Does tool support make sense for a generic tool like this?

## References
- [RAG with MariaDB](https://mariadb.org/rag-with-mariadb-vector/)
- [MCP Alchemy](https://github.com/runekaagaard/mcp-alchemy)