###Configuration directories
There are following configuration directories where LCLI is looking for configuration:
- code-source location, this is under ./src/config
- user's home directory ~/.config/.lcli
- working directory ./.lcli
All configuration are loaded in the above order and the configuration si overwritten in the top to bottom order. 
Log story short a lcli defined command could be overwritten on entire user cli or for a given directory.
For now overwriting is not tested for appending properties on an existing command.
 
###Configuration structure
The commands key is defining all the available commands available for LCLI. 
And this is a collection of commands objects with the following structure:

####Command configuration
- description used to show documentation on command
- type

  - The type of the command, defining the handler responsible to run the command
    
    - available types:
     
      - lcli - this is a lcli object tool type usually extended from lcli.tools.Base.BaseTool. 
        In this case the Python object is fully responsible.

        ```
            git:
                type: lcli
                args:
                  command: lcli.tools.Git.Git
        ```
        
      - wrapper
       
            - this allow the command to be instantiated with the args/wrapper type of wrapper object. Custom wrappers could be configured.
            - usually has multiple commands under commands key
            
            ```
              gitw:
                type: wrapper
                description: "Git vcs management - wrapped commands"
                args:
                  wrapper: base_wrapper
                  command: git
                commands:
                  save:
                    type: cli
                    description: Save current state
                    args:
                      command: 'git commit -am "${autocommit_message}" && git push origin '
                  diff:
                    type: cli
                    description: File changes
                    args:
                      command: git diff
            ```
        - function - define a Python function without any dependency
            ```
            -version:
                type: function
                args:
                  command: lcli.tools.Version.version
             ```
    - args - this are the parameters passed to the responsible code of the command, or used to construct the executable object.
        - Under args parameters you can see various type of configuration:
            - command is used depending on the type for example bellow this parameter set the shell command to execute on invocation 
            - params are used to ask push parameters on the above command, depending on it's type is iteratively asked or get from variables 
         
```
commands:
    magento:
        type: cli
        description: shell magento tools
        args:
          wrapper: base_wrapper
          command: ./m2-cluster magento
          params:
            subcommand:
              type: list
              name: ""
              message: "Choose a sub-command: "
              choices:
                - name: cache:flush
                  value: cache:flush
                - name: setup:upgrade
                  value: setup:upgrade
            message:
              message: 'Enter a commit message: '
              type: input
              name: -m
              validate: PhoneNumberValidator
              output_format: "\"$value\""
```

####Command parameters configuration
- name: name of the parameter on the command line
- message: the question asked for the parameter
- type: type of a parameter:
    - list: choose from a list of choices
    - input: read text from keyboard
- choices: list of name/value choices
- output_format: the format of output printed in command line
- validate: - not implemented for now
 