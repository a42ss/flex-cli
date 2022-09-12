from lcli.command.builders import (
    CommandBuilderFactory,
    LcliBuilder,
    SimpleBuilder,
    WrappersBuilder,
)


CommandBuilderFactory.register_builder(LcliBuilder)
CommandBuilderFactory.register_builder(SimpleBuilder)
CommandBuilderFactory.register_builder(WrappersBuilder)
