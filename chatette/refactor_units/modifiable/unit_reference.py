# coding: utf-8
"""
Module `chatette.refactor_units.modifiable.unit_reference`
Contains a class representing all the references to unit definition
that are present in template rules.
"""

from chatette.refactor_units.modifiable import ModifiableItem
from chatette.refactor_units.ast import AST


class UnitReference(ModifiableItem):
    """
    Represents a reference to a unit definition that can be contained
    in a template rule.
    """
    def __init__(self, identifier, unit_type, leading_space, modifiers):
        self._unit_type = unit_type
        super(UnitReference, self).__init__(
            identifier, leading_space, modifiers
        )
        try:
            self._definition = AST.get_or_create()[unit_type][identifier]
            self._fix_arg_value_modifier()
        except KeyError:
            self._definition = None
        
    
    def _compute_full_name(self):
        return "reference to " + self._unit_type.value + " '" + \
            self._name + "'"
    

    def get_definition(self):
        if self._definition is None:
            try:
                self._definition = \
                    AST.get_or_create()[self._unit_type][self._name]
                self._fix_arg_value_modifier()
            except KeyError:
                raise KeyError(
                    "Couldn't find the definition corresponding to " + \
                    self.full_name + "."
                )
        return self._definition

    
    def _compute_nb_possibilities(self):
        return self.get_definition().get_max_nb_possibilities()
    
    def _generate_random_strategy(self):
        return self.get_definition().generate_random()
    
    def _generate_all_strategy(self):
        return self.get_definition().generate_all()
    
    def _generate_n_strategy(self, n):
        return self.get_definition().generate_nb_possibilities(n)


    def _fix_arg_value_modifier(self):
        """
        Transforms the modifier representation to have a mapping between
        an argument name and value rather than the value only.
        This method has no effect if:
            - no argument value is set.
            - a mapping is already set as this modifier.
            - the definition doesn't exist yet.
        @raises: - `SyntaxError` if the definition does not have an argument.  # TODO should it be just a warning?
                 - `SyntaxError` if the definition has more than one argument
                   defined.
        """
        if self._definition is not None:
            if (
                self._modifiers_repr.argument_value is not None
                and not isinstance(self._modifiers_repr.argument_value, dict)
            ):
                arg_name = self._definition._modifiers_repr.argument_name
                if arg_name is None:
                    raise SyntaxError(
                        self.full_name.capitalize() + " was given an argument " + \
                        "while the definition it references has no argument " + \
                        "defined."
                    )
                if isinstance(arg_name, list):
                    raise SyntaxError(
                        self.full_name.capitalize() + " was given a single " + \
                        "unnamed argument, while the definition " + \
                        "it references defines several arguments."
                    )
                mapping = {arg_name: self._modifiers_repr.argument_value}  # TODO make that an OrderedDict to avoid having problems with arg names that are the same as the start of other ones (order the keys in descendent length of arg name)
                self._modifiers_repr.argument_value = mapping
