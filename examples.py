def context_request():
    return """
Here is an example of a smart assistant appropriately requesting more context
|start_of_example|
User: I want to do the following: connect to docker shell
The provided information is not enough to understand which exact docker container they want to connect to.
So, instead of suggesting a command with <container_name>, we can ask for more context to see possible container names.

Assistant: docker ps # for context
|end_of_example|

Here is another example when it is appropriate to ask for more context
|start_of_example|
User: I want to do the following: run main
Here is the last executed command (it may not be helpful to this request): cd ..
The current directory is: /home/user/some/path

Assistant: ls # for context
|end_of_example|

Another example:
|start_of_example|
User: 
Please fix this shell command: cd mxai
This command's current output: 
-bash: cd: mxai: No such file or directory
end of output.

Assistant: 
cd "$(ls -a | grep 'mxai' | head -n 1)"
ls # for context
find . -type d -name '*mxai*' | head -n 3 # for context
|end_of_example|
Here, an incorrect answer by the assistant would be "cd Mxai" (or similar), unless other information points to the existance of such directory. 
"""