#coding: utf8
import unittest
#from conf import NginxConfig
from blocks import KeyValueOption, KeyOption, Block
'''
s = """server {
    nameserver 123;
}"""

s = """server 123;"""


a = NginxConfig()
a.load(s)
print(a.server)
#print(a.server.nameserver)
'''


class NgKVB(Block):
    kv = KeyValueOption('kv_value')


class Test(unittest.TestCase):
    def test_base(self):
        a1 = NgKVB()
        a2 = NgKVB()
        self.assertEqual(str(a1.kv), 'kv_value')
        self.assertEqual(str(a2.kv), 'kv_value')
        self.assertEqual('kv' in a1._options, True)
        self.assertEqual('kv' in a2._options, True)
        self.assertEqual(type(a1.kv), KeyValueOption)
        self.assertEqual(type(a2.kv), KeyValueOption)
        a1.kv = 'kv_another_value'
        self.assertEqual(type(a1.kv), KeyValueOption)
        self.assertEqual(id(a1.kv) == id(KeyValueOption), False)
        self.assertEqual(id(a2.kv) == id(KeyValueOption), False)
        self.assertEqual(str(a1.kv), 'kv_another_value')
        self.assertEqual(str(a2.kv), 'kv_value')

    def test_kv_option(self):
        kv = KeyValueOption('value')
        self.assertEqual(kv.render('kv_name'), '\nkv_name = value;')
        self.assertEqual(kv.render('kv_name', indent_level=1), '\n    kv_name = value;')
        self.assertEqual(kv.render('kv_name', indent_level=2, indent_char='\t', indent=1), '\n\t\tkv_name = value;')

    def test_k_option(self):
        k = KeyOption()
        self.assertEqual(k.render('name'), '\nname;')
        self.assertEqual(k.render('name', indent_level=1), '\n    name;')
        self.assertEqual(k.render('name', indent_level=2, indent_char='\t', indent=1), '\n\t\tname;')

    def test_kv_block(self):
        kvb = Block()
        kvb.kv = KeyValueOption('value')
        self.assertEqual(kvb.render('kbv_name'), 'kbv_name {\n    kv = value;\n}')

    def test_kv_block_initial(self):
        kvb = NgKVB()
        self.assertEqual(str(kvb.kv), 'kv_value')
        self.assertEqual(kvb.kv.render('kv'), '\nkv = kv_value;')
        self.assertEqual(kvb.render('kvb_name'), 'kvb_name {\n    kv = kv_value;\n}')

        kvb.kv = 'kv_another_value'
        self.assertEqual(type(kvb.kv), KeyValueOption)
        self.assertEqual(str(kvb.kv), 'kv_another_value')
        self.assertEqual(kvb.kv.render('kv'), '\nkv = kv_another_value;')
        self.assertEqual(kvb.render('kvb_name'), 'kvb_name {\n    kv = kv_another_value;\n}')

        del kvb.kv
        self.assertEqual(hasattr(kvb, 'kv'), False)
        self.assertEqual('kv' in kvb._options, False)
        self.assertEqual(kvb.render('kvb_name'), 'kvb_name {\n}')

        kvb2 = NgKVB()
        self.assertEqual(str(kvb2.kv), 'kv_value')
        self.assertEqual(kvb2.kv.render('kv'), '\nkv = kv_value;')
        self.assertEqual(kvb2.render('kvb_name'), 'kvb_name {\n    kv = kv_value;\n}')


if __name__ == "__main__":
    unittest.main()
