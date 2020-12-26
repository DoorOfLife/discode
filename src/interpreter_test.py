import unittest
from interpreter import Interpreter


class InterpreterTest(unittest.TestCase):

    def test_execute(self):
        inter = Interpreter()
        result = inter.execute('return(hello world!)', "")
        self.assertEqual("hello world!", result)
        inter = Interpreter()
        result2 = inter.execute('return  hello world!', "")
        self.assertEqual("hello world!", result2)

        inter = Interpreter()
        result3 = inter.execute('a=hello bicycle!\nreturn($a)', "")
        self.assertEqual("hello bicycle!", result3)

        inter = Interpreter()
        result4 = inter.execute('b=split($in)\nreturn $b[0]', "hello advanced!\nblabla")
        self.assertEqual("hello advanced!", result4)

        inter = Interpreter()
        result5 = inter.execute('b=split($in)\nreturn $b[rand]', "hello advanced!\nblabla")
        self.assertIsNotNone(result5)

        inter = Interpreter()
        result6 = inter.execute('b=split($in)\nc=$b[rand]+$b[rand]\nreturn $c', "one\ntwo\nthree\nfour\nfive\nsix\nseven\neight\nnine\nten")
        self.assertIsNotNone(result6)
        print(result6)

        inter = Interpreter()
        result7 = inter.execute('b=split($in)\nreturn $b[rand]+$b[rand]', "one\ntwo\nthree\nfour\nfive\nsix\nseven\neight\nnine\nten")
        self.assertIsNotNone(result7)
        print(result7)

    def test_expand_params(self):
        inter = Interpreter()
        inter.execute_assignment("a = snaggletooth")
        expanded = inter.expand_function_params("func($a)")
        self.assertEqual('func', expanded[0])
        self.assertEqual('snaggletooth', expanded[1])
        expanded = inter.expand_function_params('my_func("hello there "+sting)')
        self.assertEqual('my_func', expanded[0])
        self.assertEqual('hello there sting', expanded[1])
        inter.variables["list_test"] = ["one", "two", "three", "four"]
        expanded = inter.expand_function_params('muy_foinc($list_test[0])')
        self.assertEqual('muy_foinc', expanded[0])
        self.assertEqual('one', expanded[1])

        expanded = inter.expand_function_params('muy_foinc($list_test[3])')
        self.assertEqual('muy_foinc', expanded[0])
        self.assertEqual('four', expanded[1])

        expanded = inter.expand_function_params('muy_foinc($list_test[4])')
        self.assertEqual('muy_foinc', expanded[0])
        self.assertEqual(None, expanded[1])

        # function with list item param, with variable as index
        inter.execute_assignment("a = 1")
        expanded = inter.expand_function_params('func($list_test[$a])')
        self.assertEqual('func', expanded[0])
        self.assertEqual("two", expanded[1])

        # test list without index
        expanded = inter.expand_function_params('func($list_test)')
        self.assertEqual('func', expanded[0])
        self.assertEqual(inter.variables['list_test'], expanded[1])

    def test_execute_function(self):
        inter = Interpreter()

        result = inter.execute_function_call('split("hello.and.goodbye", ".")')
        self.assertEqual('hello', result[0])
        self.assertEqual('and', result[1])
        self.assertEqual('goodbye', result[2])

        result = inter.execute_function_call('split("hello,and,goodbye", ",")')
        self.assertEqual('hello', result[0])
        self.assertEqual('and', result[1])
        self.assertEqual('goodbye', result[2])


    def test_execute_assignment(self):
        inter = Interpreter()
        inter.execute_assignment("a = snaggletooth")
        self.assertEqual('snaggletooth', inter.variables["a"])
        inter.execute_assignment("a2=snaggletooth2")
        self.assertEqual('snaggletooth2', inter.variables["a2"])
        inter.execute_assignment("a3=snaggletooth multiple words!")
        self.assertEqual('snaggletooth multiple words!', inter.variables["a3"])
        inter.execute_assignment('b = "hi there "')
        self.assertEqual('hi there ', inter.variables["b"])
        inter.execute_assignment('c = $b + $a + " mc\'foe!"')
        self.assertEqual("hi there snaggletooth mc'foe!", inter.variables["c"])


    def test_determine_statement_type(self):
        inter = Interpreter()
        assignment = inter.determine_statement_type("a=b")
        self.assertEqual("ASSIGNMENT", assignment)
        assignment_2 = inter.determine_statement_type("a = b ")
        self.assertEqual("ASSIGNMENT", assignment_2)

        assignment_2 = inter.determine_statement_type("a = hello world! ")
        self.assertEqual("ASSIGNMENT", assignment_2)

        assignment_3 = inter.determine_statement_type("a = $mylist[rand] ")
        self.assertEqual("ASSIGNMENT", assignment_3)

        assignment_4 = inter.determine_statement_type("a = $return[rand] ")
        self.assertEqual("ASSIGNMENT", assignment_4)

        return_statement = inter.determine_statement_type("return fart")
        self.assertEqual("RETURN", return_statement)
        return_statement_2 = inter.determine_statement_type("return $fart")
        self.assertEqual("RETURN", return_statement_2)

        return_statement_3 = inter.determine_statement_type("return $fart[$num]")
        self.assertEqual("RETURN", return_statement_3)

        rand_list_access = inter.determine_statement_type("$mylist[rand] ")
        self.assertEqual("RAND_LIST_ACCESS", rand_list_access)

        rand_list_access_2 = inter.determine_statement_type("mylist[rand] ")
        self.assertEqual("UNDEFINED", rand_list_access_2)

        index_list_access = inter.determine_statement_type("$mylist[1] ")
        self.assertEqual("INDEX_LIST_ACCESS", index_list_access)

        index_list_access_2 = inter.determine_statement_type("$mylist[24] ")
        self.assertEqual("INDEX_LIST_ACCESS", index_list_access_2)

        variable_list_access = inter.determine_statement_type("$mylist[$num] ")
        self.assertEqual("VARIABLE_LIST_ACCESS", variable_list_access)

        function_call = inter.determine_statement_type("rand()")
        self.assertEqual("FUNCTION_CALL", function_call)

        function_call = inter.determine_statement_type("return(blabla! blabla!)")
        self.assertEqual("FUNCTION_CALL", function_call)

        addition = inter.determine_statement_type("$myStr[rand] + $myOtherStr")
        self.assertEqual("ADDITION", addition)

        addition2 = inter.determine_statement_type("$myStr[rand]+$myOtherStr ")
        self.assertEqual("ADDITION", addition2)

        addition3 = inter.determine_statement_type("hello there + hello other there")
        self.assertEqual("ADDITION", addition3)

        addition4 = inter.determine_statement_type("hello there + hello other there + hello other there number three")
        self.assertEqual("ADDITION", addition4)

        literal = inter.determine_statement_type('" "')
        self.assertEqual("LITERAL", literal)

        literal2 = inter.determine_statement_type('"hello "')
        self.assertEqual("LITERAL", literal2)


    def test_variable_assignment(self):
        inter = Interpreter()
        inter.variable_assignment("a", "b")
        self.assertEqual(inter.variables.get("a"), "b")
        inter.variable_assignment("a", "c")
        self.assertEqual(inter.variables.get("a"), "c")


    def test_add_value_to_variable(self):
        inter = Interpreter()
        inter.add_value_to_variable("a", "b")
        self.assertEqual(inter.variables.get("a"), "b")
        inter.add_value_to_variable("a", "c")
        inter.add_value_to_variable("a", "d")
        inter.add_value_to_variable("a", "a")

        self.assertIn("b", inter.variables.get("a"))
        self.assertIn("c", inter.variables.get("a"))
        self.assertIn("d", inter.variables.get("a"))
        self.assertIn("a", inter.variables.get("a"))


    if __name__ == '__main__':
        unittest.main()
