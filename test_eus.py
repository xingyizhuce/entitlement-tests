import unittest


# Create our test suite.
def eus_suite():
    suite = unittest.TestSuite()
    return suite

# Launch our test suite
if __name__ == '__main__':
    # python test_eus.py
    # suite = eus_suite()
    # runner = unittest.TextTestRunner()
    # result = runner.run(suite)

    # nosetests test_eus.py
    eus_suite()


