import env  # noqa
from nose import tools
from wumai import api


class Test:

    @classmethod
    def setup_class(cls):
        cls.service = api.create()

    def setup(self):
        env.reset_db()
        self.wumai = self.service.service.test_client()

    def test_base(self):
        result = self.wumai.get('/')
        tools.assert_equal(200, result.status_code)

        result = self.wumai.post('/')
        tools.assert_equal(200, result.status_code)
