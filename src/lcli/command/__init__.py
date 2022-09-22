from lcli.command.builders import (
    CommandBuilderFactory,
    LcliBuilder,
    SimpleBuilder,
    WrappersBuilder,
)
from flex_ansible.command.wrapper.ansible import AnsibleWrapper

CommandBuilderFactory.register_builder(LcliBuilder)
CommandBuilderFactory.register_builder(SimpleBuilder)
CommandBuilderFactory.register_builder(WrappersBuilder)
CommandBuilderFactory.register_builder(WrappersBuilder)
CommandBuilderFactory.register_builder(AnsibleWrapper)
