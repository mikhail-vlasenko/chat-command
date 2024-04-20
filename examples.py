def context_request():
    return """
Here is an example of requesting more context
|start_of_example|
User: I want to do the following: connect to docker shell
The provided information is not enough to understand which exact docker container they want to connect to.
So, instead of suggesting a command with <container_name>, we can ask for more context to see possible container names.

Assistant: [context] docker ps
|end_of_example|
"""