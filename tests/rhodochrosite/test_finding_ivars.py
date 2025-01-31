# pyright: reportImplicitOverride=false

import attr

from rhodochrosite.ruby import RubyNonSpecialObject, RubySymbol, ruby_name, ruby_skip


def test_finding_normal_ivars() -> None:
    @attr.define
    class NormalType(RubyNonSpecialObject):
        field: str = attr.field()

        @property
        def ruby_class_name(self) -> RubySymbol:
            raise NotImplementedError

    fields = NormalType(field="abc").find_instance_variables()
    assert fields == [(RubySymbol("@field"), "abc")]


def test_finding_skipped_ivars() -> None:
    @attr.define
    class NormalType(RubyNonSpecialObject):
        field: str = attr.field(metadata=ruby_skip())

        @property
        def ruby_class_name(self) -> RubySymbol:
            raise NotImplementedError

    fields = NormalType(field="abc").find_instance_variables()
    assert fields == []

def test_finding_renamed_ivars() -> None:
    @attr.define
    class NormalType(RubyNonSpecialObject):
        field: str = attr.field(metadata=ruby_name("other_field"))

        @property
        def ruby_class_name(self) -> RubySymbol:
            raise NotImplementedError

    fields = NormalType(field="abc").find_instance_variables()
    assert fields == [(RubySymbol("@other_field"), "abc")]
