"""
PyDetex
https://github.com/ppizarror/pydetex

TEST UTILS
Test utils.
"""

from test._base import BaseTest

import pydetex.utils as ut
from typing import Tuple


class UtilsTest(BaseTest):

    def test_lang(self) -> None:
        """
        Test language recognition.
        """
        s = """From anchor-based frameworks, Wu et al. [1] used Mask-RCNN [2] to vectorize the walls
            by finding a rectangle proposal representing each segment's width, thickness, angle,
            and location. """
        self.assertEqual(ut.detect_language(s), 'en')
        self.assertEqual(ut.get_language_tag('en'), 'English')
        self.assertEqual(ut.get_language_tag('es'), 'Spanish')
        self.assertEqual(ut.get_language_tag('unknown'), 'Unknown')
        s = """El modelo propuesto contiene diferentes métricas para coordenar las tareas de segmentación"""
        self.assertEqual(ut.detect_language(s), 'es')
        self.assertEqual(ut.detect_language(''), '–')
        self.assertEqual(ut.detect_language('https://epic.com'), '–')

    def test_repeat_words(self) -> None:
        """
        Test repeated words.
        """
        # Test basic
        s = 'Abierto abierto abierto'
        t = 'Abierto <repeated:1>abierto</repeated> <repeated:1>abierto</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'es', 3, 15, True, True), t)

        # Ignore
        self.assertEqual(ut.check_repeated_words(s, 'es', 3, 15, True, True, ['Abierto']), s)

        s = 'The authors proposed a model which consider many semantic things, but overall the proposal is not good'
        t = 'The authors proposed a model which consider many semantic things, but overall the <repeated:11>proposal</repeated> is not good'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True), t)
        self.assertEqual(ut.check_repeated_words(s, 'unk', 3, 15, True, True), s)  # Unknown language

        s = 'Los autores propusieron un modelo sintáctico, sin embargo, éste se descartó. Descartando esto'
        t = 'Los autores propusieron un modelo sintáctico, sin embargo, éste se descartó. <repeated:1>Descartando</repeated> esto'
        self.assertEqual(ut.check_repeated_words(s, 'es', 3, 15, True, True), t)

        s = 'Le français est parlé, en 2018, sur tous les continents par environ 300 millions de personnes qui personne parle'
        t = 'Le français est parlé, en 2018, sur tous les continents par environ 300 millions de personnes qui <repeated:2>personne</repeated> <repeated:15>parle</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'fr', 3, 15, True, True), t)

        s = 'أسماء أخرى: لغة فرنسية؛ اللغة الفرنسية؛ فرنسية'
        t = 'أسماء أخرى: لغة فرنسية؛ اللغة الفرنسية؛ <repeated:3>فرنسية</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'ar', 3, 15, True, True), t)

        s = 'fremtrædende Fransk er udbredt i diplomatiet og har en fremtrædende position i den Europæiske Union'
        t = 'fremtrædende Fransk er udbredt i diplomatiet og har en <repeated:9>fremtrædende</repeated> position i den Europæiske Union'
        self.assertEqual(ut.check_repeated_words(s, 'da', 3, 15, True, True), t)

        s = 'Dies Frankreich liegt unter anderem daran, dass Frankreich ein Gründungsmitglied'
        t = 'Dies Frankreich liegt unter anderem daran, dass <repeated:6>Frankreich</repeated> ein Gründungsmitglied'
        self.assertEqual(ut.check_repeated_words(s, 'de', 3, 15, True, True), t)

        s = 'мнение о себе в мире, используется он всё меньше и меньше. В ООН Агентство Франкофонии используется'
        t = 'мнение о себе в мире, используется он всё меньше и <repeated:2>меньше.</repeated> В ООН Агентство Франкофонии <repeated:10>используется</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'ru', 3, 15, True, True), t)

        # Test with removed tokens
        s = 'This should not be repeated [NOT_REPEAT][NOT_REPEAT]a [OTHER_TAG][OTHER_TAG] [NOT_REPEAT][NOT_REPEAT]a'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True, remove_tokens=['[NOT_REPEAT]']), s)

        # Test with commands
        s = 'These commands \\texttt be removed \\texttt not \\texttt \\texttt \\texttt'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True), s)

    def test_split_tags(self) -> None:
        """
        Test split.
        """
        s = '[TAG1]new line[TAG2]this is[TAG1]very epic'
        self.assertEqual(ut.split_tags(s, ['[TAG1]', '[TAG2]']),
                         [('[TAG1]', 'new line'), ('[TAG2]', 'this is'), ('[TAG1]', 'very epic')])

        s = '[TAG1]new line[TAG1]this is[TAG1]very epic'
        self.assertEqual(ut.split_tags(s, ['[TAG1]', '[TAG2]']), [('[TAG1]', 'new linethis isvery epic')])

        # Merged tags
        s = '[TAG1]new line[TAG2][TAG2]this is[TAG1]very epic'
        self.assertEqual(ut.split_tags(s, ['[TAG1]', '[TAG2]']),
                         [('[TAG1]', 'new line'), ('[TAG2]', 'this is'), ('[TAG1]', 'very epic')])

        # No tags
        self.assertEqual(ut.split_tags(s, ['[TAG]']), [('[TAG]', '[TAG1]new line[TAG2][TAG2]this is[TAG1]very epic')])

        # Complex tagged
        s = '<A>This is a complex<B>example<A>but however <A>we should focus on<C>these<B>ideas<A>and<B>core <B>concepts<A>yes'
        self.assertEqual(ut.split_tags(s, ['<A>', '<B>', '<C>']),
                         [('<A>', 'This is a complex'), ('<B>', 'example'), ('<A>', 'but however we should focus on'),
                          ('<C>', 'these'), ('<B>', 'ideas'), ('<A>', 'and'), ('<B>', 'core concepts'), ('<A>', 'yes')])

    def test_validate(self) -> None:
        """
        Test validate.
        """
        self.assertTrue(ut.validate_int(''))
        self.assertTrue(ut.validate_int('-'))
        self.assertTrue(ut.validate_int('1'))
        self.assertTrue(ut.validate_int('-1'))
        self.assertTrue(ut.validate_int('-1.0000000000'))
        self.assertFalse(ut.validate_int('-1.01'))
        self.assertFalse(ut.validate_int('eee'))
        self.assertTrue(ut.validate_float('1'))
        self.assertTrue(ut.validate_float(''))
        self.assertTrue(ut.validate_float('-'))
        self.assertTrue(ut.validate_float('1.324'))
        self.assertTrue(ut.validate_float('-0.000123'))
        self.assertFalse(ut.validate_float('-0.123e'))

    def test_button_text(self) -> None:
        """
        Test button text.
        """
        self.assertEqual(ut.button_text('test'), 'test' if ut.IS_OSX else '  test  ')

    def test_apply_tag_between(self) -> None:
        """
        Test apply tags between.
        """
        self.assertEqual(
            ut.apply_tag_between_inside('This is a $formula$ and this is not', ('$', '$'), ('a', 'b', 'c', 'd')),
            'This is a a$bformulac$d and this is not')
        self.assertEqual(
            ut.apply_tag_between_inside('$formula$', ('$', '$'), ('X', '', '', 'X')),
            'X$formula$X')
        self.assertEqual(ut.apply_tag_between_inside('$formula$', ('$', '$'), ''), '$formula$')
        self.assertEqual(ut.apply_tag_between_inside('$formula$', ('$', '$'), 'a'), 'a$aformulaa$a')
        self.assertEqual(ut.apply_tag_between_inside('$formula$ jaja $x$', ('$', '$'), 'a'),
                         'a$aformulaa$a jaja a$axa$a')
        self.assertEqual(
            ut.apply_tag_between_inside('$form\\$ula$', ('$', '$'), ('X', '', '', 'X'), True),
            'X$form\\$ula$X')
        self.assertEqual(
            ut.apply_tag_between_inside('\\$formula\\$', ('$', '$'), ('X', '', '', 'X'), True),
            '\\$formula\\$')

        self.assertEqual(ut.apply_tag_between_inside('$formula$ jaja $x$', ('$', '$'), ('a', '', '', 'b')),
                         'a$formula$b jaja a$x$b')

    def test_find_tex_commands(self) -> None:
        """
        Test find tex commands.
        """

        def _test(_s: str, _query: Tuple[str, ...] = (), par=('{', '}')) -> None:
            _k = ut.find_tex_commands(_s, par)
            self.assertEqual(len(_k), len(_query))
            if len(_query) == 0:
                self.assertEqual(_k, ())
            else:
                for _j in range(len(_query)):
                    self.assertEqual(_s[_k[_j][1] + 2:_k[_j][2] + 1], _query[_j])

        # Test empty
        _test('This is \\a0Command{nice}')
        _test('This is \\ {nice}')
        _test('This is \\aComm\nand{nice}')
        _test('This is \\aCommand\{nice}')
        _test('This is \\aCommand{nice invalid!')
        _test('This is \\aCommand{nice invalid! \\anothercommand{yes}!')

        # Test simple
        _test('This is \\aCommand{nice}', ('nice',))
        _test('This is \\aCommand \\aCommand{nice2}', ('nice2',))
        _test('This is \\aCommand\\{ \\aCommand{nice2}', ('nice2',))
        _test('This is \\aCommand{ \\aCommand{nice2}}', (' \\aCommand{nice2}',))
        _test('This is \\aCommand{not \\} close} nice', ('not \\} close',))
        _test('This is \\aCommand{nice invalid! \\anothercommand{yes}}!',
              ('nice invalid! \\anothercommand{yes}',))
        _test('This is \\aCommand{\\command{inside}} nice',
              ('\\command{inside}',))

        # Test nested
        _test('\\a{{{{{{b}}}}}} c', ('{{{{{b}}}}}',))
        _test('\\a{{{{{{b}}}}} c}', ('{{{{{b}}}}} c',))
        _test('\\a{\\b{D}\\c{E}}', ('\\b{D}\\c{E}',))
        _test('\\a{\\b{D\\c{E}}}', ('\\b{D\\c{E}}',))

        # Test multiple
        _test('\\a{b} \\c{d}', ('b', 'd'))
        _test('\\a{\\c{d}} \\e{f}', ('\\c{d}', 'f'))
        _test('\\a{\\c{d}} \\e{{f}}', ('\\c{d}', '{f}'))
        _test('\\a{\\c{d}}\\e{{f}}', ('\\c{d}', '{f}'))
        _test('\\a{\\c{d}\\}\\{} \\e{{f}}', ('\\c{d}\\}\\{', '{f}'))

        # Other parenthesis
        _test('\\a[b] \\c[d]', ('b', 'd'), par=('[', ']'))

    def test_find_tex_commands_no_argv(self) -> None:
        """
        Test find tex commands without arguments.
        """

        def _test(_s: str, _query: Tuple[str, ...] = ()) -> None:
            _k = ut.find_tex_commands_noargv(_s)
            self.assertEqual(len(_k), len(_query))
            if len(_query) == 0:
                self.assertEqual(_k, ())
            else:
                for _j in range(len(_query)):
                    self.assertEqual(_s[_k[_j][0]:_k[_j][1] + 1], _query[_j])

        _test('This is \\acommand', ('\\acommand',))
        _test('This is \\acommand ', ('\\acommand',))
        _test('This is \\acommand{no} epic')
        _test('This is \\acommand[', ('\\acommand',))
        _test('This is \\acommand\\', ('\\acommand',))
        _test('This is \\a\\b', ('\\a', '\\b'))
        _test('This is \\\\\\\\\\\\\\\\\\a', ('\\a',))
        _test('This is \\a\\\\\\\\\\\\\\\\b', ('\\a', '\\b'))
        _test('This is \\a \\\\\\\\\\\\\\\\b', ('\\a', '\\b'))
        _test('This is \\0 \\\\\\\\\\\\\\\\b', ('\\b',))
        _test('This is \\   \\\\\\\\\\\\\\\\b', ('\\b',))
        _test('This is \\a{}\\\\\\\\\\\\\\\\b', ('\\b',))
        _test('This is \\a{\\c}\\\\\\\\\\\\\\\\d', ('\\c', '\\d',))
        _test('This is \\acommand{\\no} epic', ('\\no',))
        _test('This is \\acommand{\\no{}\\no{}} epic')
        _test('This is \\acommand{\\no{a}\\no{b}} epic')
        _test('This is \\acommand{\\1} epic')
        _test('This is \\ \\ \\1 \\2 \\_')
        _test('This is \\acommand{\\no{\\a}\\no{b}} epic', ('\\a',))
        _test('This is \\acommand{\\no{\\a{}}\\no{b}} epic')
        _test('This is \\acommand{\\no{\\a{\\c}}\\no{b}} epic', ('\\c',))
        _test('This is \\acommand{\\no{\\a{\\c1234}}\\no{b}} epic', ('\\c',))
        _test('nice \\c', ('\\c',))
        _test('\\c', ('\\c',))
        _test('\\\\')
        _test('This is a \\formula', ('\\formula',))

    def test_apply_tag_tex_commands(self) -> None:
        """
        Test tag tex commands.
        """
        s = 'This does not contain any command'
        self.assertEqual(ut.apply_tag_tex_commands(s, ''), s)

        s = 'This is a \\formula{epic} and this is not'
        b = 'This is a 1\\formula2{3epic4}5 and this is not'
        self.assertEqual(ut.apply_tag_tex_commands(s, ('1', '2', '3', '4', '5')), b)

        s = 'This is a \\formula{epic} and this is not'
        b = 'This is a |\\formula|{|epic|}| and this is not'
        self.assertEqual(ut.apply_tag_tex_commands(s, '|'), b)

        s = 'This is a \\formula{epic} and this \\i{s} not'
        b = 'This is a 1\\formula2{3epic4}5 and this 1\\i2{3s4}5 not'
        self.assertEqual(ut.apply_tag_tex_commands(s, ('1', '2', '3', '4', '5')), b)

        s = 'This is a \\formula{\\epic{nice}} and this is not'
        b = 'This is a 1\\formula2{3\\epic{nice}4}5 and this is not'
        self.assertEqual(ut.apply_tag_tex_commands(s, ('1', '2', '3', '4', '5')), b)

        s = 'This is a \\formula{nice}'
        b = 'This is a 1\\formula2{3nice4}5'
        self.assertEqual(ut.apply_tag_tex_commands(s, ('1', '2', '3', '4', '5')), b)

        s = 'This is a \\formula{\\formula{nice}}'
        b = 'This is a 1\\formula2{3\\formula{nice}4}5'
        self.assertEqual(ut.apply_tag_tex_commands(s, ('1', '2', '3', '4', '5')), b)

    def test_apply_tag_tex_commands_noargv(self) -> None:
        """
        Test tag tex commands no arguments.
        """
        s = 'This does not contain any command'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ''), s)

        s = 'This does not contain any \\command{command!}'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ''), s)

        s = 'This is a \\formula and this is not'
        b = 'This is a 1\\formula2 and this is not'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), b)

        s = 'This is a \\formula and this is not'
        b = 'This is a |\\formula| and this is not'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, '|'), b)

        s = 'This is a \\formula and this \\i not'
        b = 'This is a 1\\formula2 and this 1\\i2 not'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), b)

        s = 'This is a \\formula{\\a{} not \\b{\\c}} and this \\i not'
        b = 'This is a \\formula{\\a{} not \\b{1\\c2}} and this 1\\i2 not'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), b)

        s = 'This is a \\formula'
        b = 'This is a 1\\formula2'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), b)

    def test_syntax_highlight(self) -> None:
        """
        Test synthax.
        """
        self.assertEqual(ut.syntax_highlight('nice'),
                         '[PYDETEX_FONT:NORMAL]nice')
        self.assertEqual(ut.syntax_highlight('nice \\epic'),
                         '[PYDETEX_FONT:NORMAL]nice [PYDETEX_FONT:TEX_COMMAND]\epic[PYDETEX_FONT:NORMAL]')
