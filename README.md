# Metabase Snippet Tool

Since https://github.com/metabase/metabase/issues/6449 isn't implemented, there is no way to get variables in models or sql snippets.
And also aren't variables in derived questions/cards aren't possible. Variables just don't work, if you don't copy the full sql.

But if you copy the full sql to a question, what is if you like to change something in all of them, where you used it?

This is, where this tools comes in. To be clear: This is a workaround, no solution!

You define an snippet area in your sql code, by putting comments at the start and end of the area you wish to have under control.

```sql
--%%mb_snippet_tool:test_qeuery.sql%% DO NOT EDIT BETWEEN HERE AND MB_SNIPPET_TOOL_END!--
SELECT TOP {{Linelimit}} FROM ...
--%%mb_snippet_tool_end%%--
```
When you now put a file "test_qeuery.sql" in the snippets folder and execute mb_snippet_tool, it will replace everything between the comments with the contents of this file.
Change the filename in the comment, put a file with that name in snippets and it will replace with that. Thats it.

## Possible/missing features:

 * It doesn't configure variables, like setting the default values and so on, so it's impossible to introduce new variables without manual work
 * It doesn't support nested snippet areas
 * Better cli interface, to set path to the snippet folder/file
 * Only tested with MSSQL
 
## Usage

 * Rename the ``example_config.toml`` to ``config.toml`` and put your config in it.
 * Run the script ``python3 mb_snippet_tool.py``
 * Option: Create an executable: ``pyinstaller mb_snippet_tool.spec``