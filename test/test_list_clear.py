# -*- coding: utf-8 -*-
import pytest
import time
import sys
import random
import cPickle as pickle
from test_base_class import TestBaseClass

aerospike = pytest.importorskip("aerospike")
try:
    from aerospike.exception import *
except:
    print "Please install aerospike python client."
    sys.exit(1)

class TestListClear(object):
    def setup_class(cls):
        """
        Setup method.
        """
        hostlist, user, password = TestBaseClass.get_hosts()
        config = {'hosts': hostlist}
        if user == None and password == None:
            TestListClear.client = aerospike.client(config).connect()
        else:
            TestListClear.client = aerospike.client(config).connect(user, password)

    def teardown_class(cls):
        TestListClear.client.close()

    def setup_method(self, method):
        for i in xrange(5):
            key = ('test', 'demo', i)
            rec = {'name': 'name%s' % (str(i)), 'contact_no': [i, i+1], 'city' : ['Pune', 'Dehli']}
            TestListClear.client.put(key, rec)

    def teardown_method(self, method):
        """
        Teardoen method.
        """
        #time.sleep(1)
        for i in xrange(5):
            key = ('test', 'demo', i)
            TestListClear.client.remove(key)

    def test_list_clear_with_correct_paramters(self):
        """
        Invoke list_clear() with correct parameters
        """
        key = ('test', 'demo', 1)

        status = TestListClear.client.list_clear(key, 'contact_no')

        assert status == 0L

        (key,meta, bins) = TestListClear.client.get(key)
        assert bins == {'city': ['Pune', 'Dehli'], 'contact_no': [], 'name': 'name1'}

    def test_list_clear_list_with_correct_policy(self):
        """
        Invoke list_clear() removes all list elements with correct policy
        """
        key = ('test', 'demo', 2)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'commit_level': aerospike.POLICY_COMMIT_LEVEL_MASTER
        }
        
        key = ('test', 'demo', 2)

        status = TestListClear.client.list_clear(key, 'city')
        assert status == 0L

        (key,meta, bins) = TestListClear.client.get(key)
        assert bins == {'city': [], 'contact_no': [2, 3], 'name': 'name2'}

    def test_list_clear_with_no_parameters(self):
        """
        Invoke list_clear() without any mandatory parameters.
        """
        with pytest.raises(TypeError) as typeError:
            TestListClear.client.list_clear()
        assert "Required argument 'key' (pos 1) not found" in typeError.value

    def test_list_clear_with_incorrect_policy(self):
        """
        Invoke list_clear() with incorrect policy
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 0.5
        }
        try:
            TestListClear.client.list_clear(key, "contact_no", {}, policy)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "timeout is invalid"

    def test_list_clear_with_nonexistent_key(self):
        """
        Invoke list_clear() with non-existent key
        """
        charSet = 'abcdefghijklmnopqrstuvwxyz1234567890'
        minLength = 5
        maxLength = 30
        length = random.randint(minLength, maxLength)
        key = ('test', 'demo', ''.join(map(lambda unused :
            random.choice(charSet), range(length)))+".com")
        try:
            TestListClear.client.list_clear(key, "contact_no")
        except BinIncompatibleType as exception:
            assert exception.code == 12L

    def test_list_clear_with_extra_parameter(self):
        """
        Invoke list_clear() with extra parameter.
        """
        key = ('test', 'demo', 1)
        policy = {'timeout': 1000}
        with pytest.raises(TypeError) as typeError:
            TestListClear.client.list_clear(key, "contact_no", {}, policy, "")

        assert "list_clear() takes at most 4 arguments (5 given)" in typeError.value

    def test_list_clear_policy_is_string(self):
        """
        Invoke list_clear() with policy is string
        """
        key = ('test', 'demo', 1)
        try:
            TestListClear.client.list_clear(key, "contact_no", {}, "")

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "policy must be a dict"

    def test_list_clear_key_is_none(self):
        """
        Invoke list_clear() with key is none
        """
        try:
            TestListClear.client.list_clear(None, "contact_no")

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "key is invalid"

    def test_list_clear_bin_is_none(self):
        """
        Invoke list_clear() with bin is none
        """
        key = ('test', 'demo', 1)
        try:
            TestListClear.client.list_clear(key, None)

        except ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "Bin name should be of type string"
